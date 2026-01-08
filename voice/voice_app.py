'''
Script to get Audio on a website. Must be ran using this command
streamlit run voice/voice_app.py
'''


import streamlit as st
import asyncio
import os
from audio_recorder_streamlit import audio_recorder
from backboard import BackboardClient
from openai import OpenAI 
from dotenv import load_dotenv
load_dotenv()

#Becuase of how we need to run the streamlit file, we cant run it like a normal module so 
#we do this nasty stuff to get the API_KEY
BACKBOARD_API_KEY = os.getenv("BACKBOARD_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if BACKBOARD_API_KEY is None:
    raise Exception("BACKBOARD_API_KEY is None")

if OPENAI_API_KEY is None:
    raise Exception("OPENAI_API_KEY is None")

# 1. Setup Clients
# You need BOTH keys. Backboard for memory, OpenAI for voice.
client_bb = BackboardClient(api_key=BACKBOARD_API_KEY)
client_oa = OpenAI(api_key=OPENAI_API_KEY)


# Async helper
def run_async(coroutine):
    return asyncio.run(coroutine)

st.title("️Voice Intake")

# Initialize Session State
if "thread_id" not in st.session_state:
   #Make sure the model exisits
   st.session_state.messages = []

# Display Conversation History
for role, text in st.session_state.messages:
    with st.chat_message(role):
        st.write(text)

# --- STEP 1: VOICE INPUT ---
# This creates a microphone button. It returns audio bytes when you stop recording.
audio_bytes = audio_recorder(text="", icon_size="2x", neutral_color="#6c757d", recording_color="#dc3545")

if audio_bytes:
    # Save the audio to a temporary file
    with open("temp_input.wav", "wb") as f:
        f.write(audio_bytes)
    
    # --- STEP 2: SPEECH TO TEXT (Whisper) ---
    with st.spinner("Listening..."):
        transcript = client_oa.audio.transcriptions.create(
            model="whisper-1", 
            file=open("temp_input.wav", "rb")
        ).text
    
    # Show what the user said
    st.session_state.messages.append(("user", transcript))
    with st.chat_message("user"):
        st.write(transcript)

    # --- STEP 3: BACKBOARD BRAIN ---
    async def get_reply():
        response = await client_bb.add_message(
            thread_id=st.session_state.thread_id,
            content=transcript
        )
        return response.latest_message.content

    ai_text = run_async(get_reply())
    
    st.session_state.messages.append(("assistant", ai_text))
    with st.chat_message("assistant"):
        st.write(ai_text)

    # --- STEP 4: TEXT TO SPEECH ---
    # This generates the audio file for the AI's reply
    with client_oa.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="shimmer",
            input=ai_text
        ) as response:
            # Now we save the stream to a file safely
            response.stream_to_file("output.mp3")
        
    # Auto-play the audio
    st.audio("output.mp3", format="audio/mp3", autoplay=True)