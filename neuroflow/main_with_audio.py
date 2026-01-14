import asyncio
import speech_recognition as sr
from gtts import gTTS
import os
import sys

# --- Existing Imports ---
from parsing import post_patient_text_to_llm
import parsing
from memory import MemoryManager 
from llm import LLMClient
from dotenv import load_dotenv
from tools.notetaker import NoteTaker

load_dotenv()

# --- Audio Helper Functions ---

def speak_response(text):
    """
    Converts text to audio using gTTS and plays it immediately.
    """
    print(f"NeuroFlow (Speaking): {text}") # Keep visual log
    
    # 1. Generate Audio
    tts = gTTS(text=text, lang='en')
    filename = "response.mp3"
    tts.save(filename)
    
    # 2. Play Audio (Platform specific)
    if sys.platform == "darwin":  # macOS
        os.system(f"afplay {filename}")
    elif sys.platform == "win32": # Windows
        os.system(f"start {filename}")
    else: # Linux
        os.system(f"mpg123 {filename}") # Requires mpg123 installed

def listen_to_patient():
    """
    Listens to the microphone and returns text.
    Blocks until speech is detected and processed.
    """
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\nListening... (Speak now)")
        # Adjust for ambient noise to prevent silence from triggering
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        try:
            # Listen for input
            audio = recognizer.listen(source, timeout=10) # 10s wait limit
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return ""
        except sr.RequestError:
            print("Could not request results (Offline?)")
            return ""
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            return ""

# --- Main Class ---

class NeuroFlowMain:
    """
    Main orchestration layer.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        memory_manager: MemoryManager,
        notetaker: NoteTaker
    ):
        self.llm = llm_client
        self.memory = memory_manager
        self.notetaker = notetaker
    
    
    async def handle_patient_message(
        self,
        thread_id: str,
        patient_text: str
    ) -> dict:
        """
        One turn of the chat loop.
        Returns response text + terminate flag.
        """

        memory_context = await self.memory.get_context(thread_id)

        parsed_txt = await post_patient_text_to_llm(
            llm_client=self.llm,
            patient_text=patient_text,
            thread_id=thread_id,
            memory_context=memory_context
        )

        parsed = parsing.parse_llm_response(parsed_txt, patient_text)

        # Store memory
        self.memory.write(thread_id, parsed.memory_candidates)

        # End-of-chat handling
        if parsed.terminate:
            await self.notetaker.generate_notes(thread_id)

        return {
            "response": parsed.response,
            "terminate": parsed.terminate
        }

async def main():
    # --- instantiate dependencies ---
    llm_client = LLMClient()
    memory_manager = MemoryManager()
    note_taker = NoteTaker()
    
    neuroflow = NeuroFlowMain(
        llm_client=llm_client,
        memory_manager=memory_manager,
        notetaker=note_taker
    )

    # --- start chat ---
    await llm_client.init_assistant()
    print("Assistant ID:", llm_client.assistant.assistant_id)
    thread_id = await llm_client.create_thread()
    print("🧠 NeuroFlow Voice Chatbot started.")

    # In your original code, you simulated the user saying "Hello" first
    # to trigger the bot's greeting. We keep this flow.
    patient_text = "Hello! How are you feeling today?" 
    
    terminate = False
    first_run = True

    while not terminate:
        # If it's NOT the first run, we need to listen for the user
        if not first_run:
            patient_text = listen_to_patient()
            
            # If listening failed or timed out, skip this loop iteration
            if not patient_text:
                continue
                
            if patient_text.lower() in ["quit", "exit", "stop"]:
                speak_response("Goodbye.")
                break

        # Process the input (either the phantom "Hello" or actual voice)
        response_dict = await neuroflow.handle_patient_message(thread_id, patient_text)
        
        # Speak the result
        speak_response(response_dict['response'])

        terminate = response_dict.get("terminate", False)
        first_run = False # Flag off after the bootstrap loop

    print("Chat ended.")

if __name__ == "__main__":
    asyncio.run(main())