import streamlit as st
import asyncio
import os 
import sys
import speech_recognition as sr
from gtts import gTTS
import tempfile
import json
from dotenv import load_dotenv

# 1. LOAD ENV
load_dotenv()

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from main import NeuroFlowMain, LLMClient, MemoryManager, NoteTaker

st.set_page_config(page_title="NeuroFlow Voice", page_icon="🧠")

# --- CACHE RESOURCES ---
@st.cache_resource
def get_memory():
    """Only cache things that hold DATA, not connections."""
    return MemoryManager(), NoteTaker()

memory_manager, note_taker = get_memory()

# --- MANUAL TERMINATION BUTTON ---
with st.sidebar:
    if st.button("End Session & Save Notes", type="primary"):
        with st.spinner("Saving session notes..."):
            
            # Define async task for termination
            async def end_session():
                # We can reuse the cached note_taker
                await note_taker.generate_notes(st.session_state.thread_id)
            
            # Run the task
            asyncio.run(end_session())
            
        st.success("Session saved and ended.")
        st.session_state.messages.append({"role": "assistant", "content": "Session manually ended. Notes saved."})
        st.stop()

# --- AUDIO HELPER FUNCTIONS ---

def transcribe_audio(audio_bytes):
    """Converts audio input bytes to text."""
    r = sr.Recognizer()
    # Write bytes to a temporary wav file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
        tmp_audio.write(audio_bytes.read())
        tmp_audio_path = tmp_audio.name

    text = ""
    try:
        with sr.AudioFile(tmp_audio_path) as source:
            # Record the audio from the file
            audio_data = r.record(source)
            # Transcribe
            text = r.recognize_google(audio_data)
    except sr.UnknownValueError:
        st.error("Could not understand audio.")
    except sr.RequestError:
        st.error("Could not request results from Google Speech Recognition service.")
    finally:
        os.remove(tmp_audio_path)
    return text

def text_to_speech_file(text):
    """Converts text to an MP3 file path."""
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_mp3:
        tts.save(tmp_mp3.name)
        return tmp_mp3.name


# --- SESSION SETUP ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Initial Greeting with Audio
    greeting = "Hello! I am NeuroFlow. How can I help?"
    greeting_audio = text_to_speech_file(greeting)
    st.session_state.messages.append({
        "role": "assistant", 
        "content": greeting, 
        "audio": greeting_audio
    })

if "thread_id" not in st.session_state:
    async def init_chat():
        temp_client = LLMClient()
        await temp_client.init_assistant()
        return await temp_client.create_thread()
    st.session_state.thread_id = asyncio.run(init_chat())

# Key to force audio widget reset
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# --- UI LOGIC ---
st.title("🧠 NeuroFlow Voice Agent")

# 1. Display Chat History (Text + Audio Players)
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "audio" in msg:
                st.audio(msg["audio"], format="audio/mp3", start_time=0)

# 2. Audio Input Widget
audio_value = st.audio_input("Record your voice", key=f"audio_{st.session_state.input_key}")

# 3. Processing Logic
if audio_value:
    # A. Transcribe
    user_text = transcribe_audio(audio_value)
    
    if user_text:
        # Append User Message
        st.session_state.messages.append({"role": "user", "content": user_text})
        
        # B. Define the Async Task
        async def get_response():
            # Create FRESH client to avoid "Event loop closed" error
            fresh_client = LLMClient()
            await fresh_client.init_assistant()
            
            flow = NeuroFlowMain(
                llm_client=fresh_client, 
                memory_manager=memory_manager, 
                notetaker=note_taker
            )
            
            # --- OVERRIDE handle_patient_message LOGIC HERE ---
            # We must implement the fix for the memory parsing error manually
            # since we can't easily edit 'main.py' from here.
            
            # 1. Get Context
            memory_context = await flow.memory.get_context(st.session_state.thread_id)
            
            # 2. Get LLM Raw Text (Using the fresh client)
            # Note: We need to import post_patient_text_to_llm for this
            from parsing import post_patient_text_to_llm
            import parsing
            
            parsed_txt = await post_patient_text_to_llm(
                llm_client=fresh_client,
                patient_text=user_text,
                thread_id=st.session_state.thread_id,
                memory_context=memory_context
            )
            
            parsed = parsing.parse_llm_response(parsed_txt, user_text)
            
            # 3. FIX: Sanitize Memory Data
            mem_candidates = parsed.memory_candidates
            if isinstance(mem_candidates, str):
                try:
                    mem_candidates = json.loads(mem_candidates)
                except json.JSONDecodeError:
                    mem_candidates = {}

            # 4. Save Memory
            await flow.memory.write(st.session_state.thread_id, mem_candidates)
            
            # 5. Check Termination
            if parsed.terminate:
                await flow.notetaker.generate_notes(st.session_state.thread_id)
            
            return {"response": parsed.response, "terminate": parsed.terminate}

        # C. Run Logic
        with st.spinner("Thinking..."):
            result = asyncio.run(get_response())
            
            response_text = result["response"]
            
            # Generate Audio for Response
            response_audio_path = text_to_speech_file(response_text)
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response_text,
                "audio": response_audio_path
            })
            
            # Increment key to reset the microphone widget
            st.session_state.input_key += 1
            
            if result["terminate"]:
                st.success("Session Ended.")
                st.stop()
            
            st.rerun()