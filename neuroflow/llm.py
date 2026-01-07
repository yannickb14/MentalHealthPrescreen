import os
import asyncio
from typing import Optional
from backboard import BackboardClient
from prompt_schemas import ParsedResponse
import prompts

def generate_response():
    raise NotImplementedError("Implement Generate Response and Import it")

async def parse_prompt_llm(text: str) -> ParsedResponse:
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

    return ParsedResponse(
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