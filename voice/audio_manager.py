import streamlit as st
from openai import OpenAI

def transcribe_audio(client: OpenAI, audio_file):
    """
    Step 1: Takes raw audio (from microphone/upload) and converts it to text.
    Returns: String (The transcribed text)
    """
    if audio_file is None:
        return None

    # Streamlit audio widgets return a BytesIO buffer, but OpenAI needs a name/mode
    # We assign a name so the API knows it's an mp3/wav
    audio_file.name = "input_audio.wav" 
    
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    
    return transcript.text

def text_to_speech(client: OpenAI, text: str, output_path: str = "output.mp3"):
    """
    Step 2: Takes the AI's text response and converts it to an audio file.
    It plays the audio automatically in Streamlit.
    """
    if not text:
        return

    # Use the 'with' block to handle streaming safely (Fixes the deprecation warning)
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="shimmer",  # Options: alloy, echo, fable, onyx, nova, shimmer
        input=text
    ) as response:
        response.stream_to_file(output_path)

    # Display/Play the audio in the app
    st.audio(output_path, format="audio/mp3", autoplay=True)