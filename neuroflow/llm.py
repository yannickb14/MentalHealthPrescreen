import os
import asyncio
from typing import Optional
from backboard import BackboardClient
from models import ParsedPrompt
import prompts

async def parse_prompt_llm(text: str) -> ParsedPrompt:
    """
    Use LLM to parse raw patient text into structured ParsedPrompt.
    Returns: ParsedPrompt object with intent, emotion, and memory candidates.
    """
    prompt = f"""
    You are a clinician AI. Analyze the patient's text and return a JSON object with:
    - intent: one of 'venting', 'question', 'report', 'reflection', 'goal', 'narrative', 'worry', 'other'
    {prompts.INTENT_DESCRIPTIONS}



    - emotion: one of:
    {prompts.EMOTION_DEFINITIONS}
    
    - memory_candidates: short_term (temporary context), long_term (clinically relevant info)
    Patient text: \"\"\"{text}\"\"\"
    """

    response_text = await generate_response(prompt)

    # Parse LLM output as JSON (assumes LLM returns valid JSON)
    import json
    data = json.loads(response_text)

    return ParsedPrompt(
        text=text,
        intent=data.get("intent"),
        emotion=data.get("emotion"),
        memory_candidates=data.get("memory_candidates", {"short_term": [], "long_term": []}),
        entities=data.get("entities", {})
    )


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

    async def generate_response(
        self,
        prompt: str,
        thread_id: Optional[str] = None,
        memory: str = "None",  # "Auto" for persistence, "None" for temporary
        stream: bool = False
    ) -> str:
        """
        Sends a prompt to the LLM and returns the response text.
        Optionally attaches to a thread for memory context.
        """
        if self.assistant is None:
            await self.init_assistant()

        if thread_id is None:
            # Create a temporary thread for single-use LLM call
            thread = await self.client.create_thread(self.assistant.assistant_id)
            thread_id = thread.thread_id

        response = await self.client.add_message(
            thread_id=thread_id,
            content=prompt,
            memory=memory,
            stream=stream
        )
        return response.content
