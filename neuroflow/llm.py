import os
import asyncio
from typing import Optional
from backboard import BackboardClient
from prompt_schemas import ParsedResponse
import prompts
import json
from typing import Dict, Any, Optional

class LLMClient:
    """
    Minimal LLM wrapper for NeuroFlow.
    Handles prompt generation and streaming responses if needed.
    """

    def __init__(self):
        self.client = BackboardClient(api_key=os.getenv("BACKBOARD_API_KEY"))
        self.assistant = None

    async def init_assistant(self, name: str = "NeuroFlow LLM", description: str = "LLM for structured parsing and response generation"):
        """
        Creates an assistant if it doesn't exist.
        """
        if self.assistant is None:
            self.assistant = await self.client.create_assistant(
                name=name,
                description=description
            )

    async def create_thread(self) -> str:
        if self.assistant is None:
            await self.init_assistant()

        thread_obj = await self.client.create_thread(assistant_id=self.assistant.assistant_id)
        return thread_obj.thread_id  # valid UUID to use in add_message


    async def generate_response(
        self,
        prompt: str,
        thread_id: Optional[str] = None,
        memory: str = "Auto",
        stream: bool = False
    ) -> str:
        """
        Calls Backboard API to generate a response for the given prompt.
        Returns the raw text of the assistant's latest message.
        """
        if self.assistant is None:
            await self.init_assistant()

        response = await self.client.add_message(
            #assistant_id=self.assistant.id, no assistant variable
            thread_id=thread_id,
            content=prompt,
            memory=memory,
            llm_provider="google",
            model_name="gemini-2.5-flash",
            stream=stream
        )

        # Return the latest message content from the assistant
        return response.content or response.message

    #POST
    async def post_prompt(
        self,
        prompt: str,
        thread_id: Optional[str] = None,
        memory: str = "Auto",
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Sends a prompt expecting JSON output.
        Returns both raw text and parsed JSON.
        """
        raw_text = await self.generate_response(
            prompt=prompt,
            thread_id=thread_id,
            memory=memory,
            stream=stream
        )
        return raw_text