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

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            raise ValueError("LLM did not return valid JSON")

        return {
            "raw_text": raw_text,
            "json": data
        }