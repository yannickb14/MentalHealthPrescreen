from llm import generate_response  # your LLM wrapper
from models import ParsedPrompt

async def parse_prompt_llm(text: str) -> ParsedPrompt:
    """
    Use LLM to parse raw patient text into structured ParsedPrompt.
    Returns: ParsedPrompt object with intent, emotion, and memory candidates.
    """
    prompt = f"""
    You are a clinician AI. Analyze the patient's text and return a JSON object with:
    - intent: one of 'venting', 'question', 'report', 'other'
    - emotion: one of 'anxious', 'sad', 'happy', 'neutral'
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
