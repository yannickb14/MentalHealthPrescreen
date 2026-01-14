import os
import sys
# --- Your Custom Imports ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir) 
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import tempfile
import asyncio
import os

import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import tempfile
import asyncio
import os
import json  # <--- NEW IMPORT

# --- Your Custom Imports ---
from parsing import post_patient_text_to_llm
import parsing
from memory import MemoryManager 
from llm import LLMClient
from dotenv import load_dotenv
from tools.notetaker import NoteTaker

load_dotenv()

# --- Page Config ---
st.set_page_config(page_title="NeuroFlow Voice", layout="centered")
st.title("🧠 NeuroFlow Voice Interface")

# --- Helper Functions ---

def transcribe_audio(audio_bytes):
    r = sr.Recognizer()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
        tmp_audio.write(audio_bytes.read())
        tmp_audio_path = tmp_audio.name

    text = ""
    try:
        with sr.AudioFile(tmp_audio_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
    except sr.UnknownValueError:
        st.error("Could not understand audio.")
    except sr.RequestError:
        st.error("Could not request results.")
    finally:
        os.remove(tmp_audio_path)
    return text

def text_to_speech_file(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_mp3:
        tts.save(tmp_mp3.name)
        return tmp_mp3.name

# --- Logic Class ---
class NeuroFlowMain:
    def __init__(self, llm_client, memory_manager, notetaker):
        self.llm = llm_client
        self.memory = memory_manager
        self.notetaker = notetaker

    async def handle_patient_message(self, thread_id, patient_text):
        memory_context = await self.memory.get_context(thread_id)
        
        parsed_txt = await post_patient_text_to_llm(
            llm_client=self.llm,
            patient_text=patient_text,
            thread_id=thread_id,
            memory_context=memory_context
        )
        
        parsed = parsing.parse_llm_response(parsed_txt, patient_text)
        
        # --- FIX STARTS HERE ---
        # Ensure memory_candidates is a dictionary, not a string
        mem_candidates = parsed.memory_candidates
        if isinstance(mem_candidates, str):
            try:
                # Try to parse stringified JSON (e.g. "{'key': 'val'}")
                mem_candidates = json.loads(mem_candidates)
            except json.JSONDecodeError:
                # If parsing fails, default to empty dict to prevent crash
                print(f"Warning: Could not parse memory_candidates: {mem_candidates}")
                mem_candidates = {}
        # --- FIX ENDS HERE ---

        await self.memory.write(thread_id, mem_candidates)
        
        if parsed.terminate:
            await self.notetaker.generate_notes(thread_id)
            
        return {"response": parsed.response, "terminate": parsed.terminate}

# --- Initialization ---

if "thread_id" not in st.session_state:
    async def get_new_thread_id():
        temp_client = LLMClient()
        await temp_client.init_assistant()
        return await temp_client.create_thread()
    
    st.session_state.thread_id = asyncio.run(get_new_thread_id())
    st.session_state.messages = []
    
    # Initial Greeting
    greeting = "Hello! How are you feeling today?"
    st.session_state.messages.append({
        "role": "assistant", 
        "content": greeting, 
        "audio": text_to_speech_file(greeting)
    })

if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# --- UI Layout ---

chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "audio" in msg:
                st.audio(msg["audio"], format="audio/mp3", start_time=0)

# --- Audio Input with Dynamic Key ---
audio_value = st.audio_input("Record your reply", key=f"audio_{st.session_state.input_key}")

if audio_value:
    user_text = transcribe_audio(audio_value)
    
    if user_text:
        st.session_state.messages.append({"role": "user", "content": user_text})
        
        async def run_conversation_turn():
            # Create FRESH instances for the new loop
            current_llm = LLMClient()
            current_mem = MemoryManager()
            current_note = NoteTaker()
            
            await current_llm.init_assistant()
            
            flow = NeuroFlowMain(current_llm, current_mem, current_note)
            
            return await flow.handle_patient_message(
                st.session_state.thread_id, 
                user_text
            )

        response_dict = asyncio.run(run_conversation_turn())
        
        bot_text = response_dict["response"]
        audio_path = text_to_speech_file(bot_text)
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": bot_text,
            "audio": audio_path
        })
        
        if response_dict.get("terminate"):
            st.warning("Chat ended by NeuroFlow.")
            st.stop()
        
        # Increment Key to Reset Widget
        st.session_state.input_key += 1
        st.rerun()