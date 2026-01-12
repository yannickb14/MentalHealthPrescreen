import os
from backboard import BackboardClient
import asyncio

class MemoryManager:
    def __init__(self):
        api_key = os.getenv("BACKBOARD_API_KEY")
        if api_key is None:
            raise Exception("BACKBOARD API KEY not found")
        self.client = BackboardClient(
            api_key=api_key
        )
        self.assistant = None #TODO, have some assisntant ID in a config file everywhere
                              #So we only craete a new one when needed.

    async def init_assistant(self):
        if self.assistant is None:
            self.assistant = await self.client.create_assistant(
                name="Neuroflow Memory",
                description="Stores clinically relevant patient context such as symptoms, preferences, emotional state, and personal history."
            )

    async def read(self, thread_id: str):
        """
        Reading memory is implicit in Backboard.
        Just return thread_id so the LLM can retrieve.
        """
        return thread_id

    async def write(self, thread_id: str, memory_candidates: dict):
        """
        Write ONLY long-term memory candidates.
        Short-term memory should stay in-session.
        """

        long_term = memory_candidates.get("long_term", [])
        if not long_term:
            return

        for item in long_term: 
            await self.client.add_memory(
                thread_id=thread_id,
                content=item,
                memory="Auto",   # Let Backboard decide storage
                stream=False
            )

    async def get_context(self, thread_id: str) -> str:
        """
        Returns a string of relevant memory to include in the prompt.
        """
        # Ensure assistant is initialized
        await self.init_assistant()

        # Read stored memories (stub for now just returns thread_id)
        # In real implementation, you would fetch long-term memory objects
        memories = await self.read(thread_id)  # this could return a list of items
        if isinstance(memories, list):
            return "\n".join(memories)
        elif isinstance(memories, str):
            return memories
        else:
            return ""
