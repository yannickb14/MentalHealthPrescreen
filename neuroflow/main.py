import asyncio
from parsing import post_patient_text_to_llm  #<- I think this? #parse_prompt_llm
from memory import MemoryManager #NeuroFlow
from llm import LLMClient
from prompt_schemas import ParsedResponse
from dotenv import load_dotenv
from tools.notetaker import NoteTaker

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

        memory_context = self.memory.get_context(thread_id)

        parsed = await post_patient_text_to_llm(
            llm_client=self.llm,
            patient_text=patient_text,
            memory_context=memory_context
        )

        # Store memory
        self.memory.write(thread_id, parsed.memory_candidates)

        # End-of-chat handling
        if parsed.terminate:
            self.notetaker.write(thread_id, self.memory)

        return {
            "response": parsed.response,
            "terminate": parsed.terminate
        }
