import os
from backboard import BackboardClient
import asyncio
from config import BACKBOARD_API_KEY

class MemoryManager:
    def __init__(self):
        self.client = BackboardClient(
            api_key=BACKBOARD_API_KEY
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

        for item in long_term: #TODO This is going to display evtg the AI is thinking to the patient
                            # Dont need the paitent to know exactly what the AI is thinking
            await self.client.add_message(
                thread_id=thread_id,
                content=item,
                memory="Auto",   # Let Backboard decide storage
                stream=False
            )
