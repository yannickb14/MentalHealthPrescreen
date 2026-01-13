import streamlit as st
import asyncio
import os 
import sys
from dotenv import load_dotenv

# 1. LOAD ENV HERE (Streamlit needs this explicitly)
load_dotenv()

# Setup paths (keep your existing code)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from main import NeuroFlowMain, LLMClient, MemoryManager, NoteTaker

st.set_page_config(page_title="NeuroFlow AI", page_icon="🧠")

# --- CHANGE 1: CACHE ONLY MEMORY (Not the Network Client) ---
@st.cache_resource
def get_memory():
    """Only cache things that hold DATA, not connections."""
    return MemoryManager(), NoteTaker()

memory_manager, note_taker = get_memory()

# --- SESSION SETUP ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Hello! I am NeuroFlow. How can I help?"})

if "thread_id" not in st.session_state:
    async def init_chat():
        # We create a temporary client just to get the thread ID
        temp_client = LLMClient()
        await temp_client.init_assistant()
        return await temp_client.create_thread()
    
    st.session_state.thread_id = asyncio.run(init_chat())

# --- UI LOGIC ---
st.title("🧠 NeuroFlow Agent")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Type here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # --- CHANGE 2: CREATE FRESH CLIENT INSIDE THE LOOP ---
    async def get_response():
        # Create a FRESH client that attaches to the CURRENT event loop
        fresh_client = LLMClient()
        
        # Initialize it (since it's new)
        await fresh_client.init_assistant()
        
        # Re-assemble the orchestrator with the fresh client + cached memory
        flow = NeuroFlowMain(
            llm_client=fresh_client, 
            memory_manager=memory_manager, 
            notetaker=note_taker
        )
        
        return await flow.handle_patient_message(
            thread_id=st.session_state.thread_id,
            patient_text=prompt
        )

    # --- CHANGE 3: RUN ---
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Now this works because everything is on the same loop!
            result = asyncio.run(get_response())
            
            response_text = result["response"]
            st.write(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            if result["terminate"]:
                st.success("Session Ended.")
                st.stop()