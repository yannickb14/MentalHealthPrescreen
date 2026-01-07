# prompt_builder.py

from prompts import INTENT_DEFINITIONS, EMOTION_DEFINITIONS, RESPONSE_INSTRUCTIONS

def build_parsing_prompt(patient_text: str, memory_context: str = "") -> str:
    """
    Build the prompt text for the LLM to parse patient input.
    
    Arguments:
        patient_text: Raw text from the patient.
        memory_context: Optional string of relevant memory (short-term or long-term) to include.

    Returns:
        A string prompt to send to the LLM.
    """


    prompt = f"""
    You are a clinician AI. Analyze the patient's text and return a JSON object with the following fields:

    - intent: one of:
    {INTENT_DEFINITIONS}

    - emotion: one of:
    {EMOTION_DEFINITIONS}

    - memory_candidates: short_term (temporary context), long_term (clinically relevant info)

    - response: text to respond back to the patient
    {RESPONSE_INSTRUCTIONS}

    Use the following patient text as input:
    \"\"\"{patient_text}\"\"\"

    Include any relevant memory context:
    \"\"\"{memory_context}\"\"\"

    Include a boolean called "terminate" indicating if the chat is over.

    Return ONLY valid JSON. Do not include explanations or extra text.
    """
    return prompt
