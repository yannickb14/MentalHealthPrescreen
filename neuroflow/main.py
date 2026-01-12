import asyncio
from parsing import post_patient_text_to_llm  #<- I think this? #parse_prompt_llm
import parsing
from memory import MemoryManager #NeuroFlow
from llm import LLMClient
from prompt_schemas import ParsedResponse
from dotenv import load_dotenv
from tools.notetaker import NoteTaker
import uuid

load_dotenv()

class NeuroFlowMain:
    """
    Main orchestration layer.
    This is the only module the frontend talks to.
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
        Returns response text + terminate flag for the frontend.
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
    thread_id = await llm_client.create_thread()  # for testing
    print("🧠 NeuroFlow Chatbot started. Type your message (or 'quit' to exit).")

    # Optionally, the chatbot can start first
    patient_text = ""
    terminate = False

    while not terminate:
        if not patient_text:
            # First message from chatbot
            patient_text = "Hello! How are you feeling today?"  # default opening
        else:
            patient_text = input("You: ")

        response_dict = await neuroflow.handle_patient_message(thread_id, patient_text)
        print(f"NeuroFlow: {response_dict['response']}")

        terminate = response_dict.get("terminate", False)

        if patient_text.lower() == "quit":
            break

    print("Chat ended.")

# Run the async main loop
if __name__ == "__main__":
    asyncio.run(main())
