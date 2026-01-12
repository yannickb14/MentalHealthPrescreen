# prompt_builder.py

from prompts import INTENT_DEFINITIONS, EMOTION_DEFINITIONS, RESPONSE_INSTRUCTIONS
from prompt_schemas import ParsedResponse, ResponsePlan
from tools.response_planner import default_response_plan, build_response_plan

def build_full_prompt(
    patient_text: str = "",
    memory_context: str = "",
    parsed: ParsedResponse | None = None
) -> str:
    """
    Build the full LLM prompt:
    - Parsing instructions (intent, emotion, memory_candidates)
    - Response plan instructions (tone, goals, constraints)
    - Patient text and optional memory context

    If parsed is None, this is the first turn and a default ResponsePlan is used.
    """

    # Step 1: Determine ResponsePlan
    plan: ResponsePlan = build_response_plan(parsed) if parsed else default_response_plan()

    # Step 2: Render ResponsePlan into text
    instructions = []
    if plan.tone:
        instructions.append(f"- Tone: {plan.tone}")
    if plan.goals:
        instructions.append("Goals:")
        for g in plan.goals:
            instructions.append(f"- {g}")
    if plan.constraints:
        instructions.append("Constraints:")
        for c in plan.constraints:
            instructions.append(f"- {c}")
    plan_text = "\n".join(instructions)

    # Step 3: Include patient text (if any) and memory context
    patient_block = f'Patient message:\n"""{patient_text}"""' if patient_text else "No patient message yet."
    memory_block = f"Memory context:\n\"\"\"{memory_context}\"\"\"" if memory_context else ""

    # Step 4: Compose full prompt
    full_prompt = f"""
    You are a clinician AI. Analyze the patient's text and return a JSON object with the following fields:

    - intent: one of:
    {INTENT_DEFINITIONS}

    - emotion: one of:
    {EMOTION_DEFINITIONS}

    - memory_candidates: short_term (temporary context), long_term (clinically relevant info)

    - response: text to respond back to the patient
    {RESPONSE_INSTRUCTIONS}

    - terminate: boolean whether the chat is over (should be indicated by patient)

    Response guidelines:
    {plan_text}

    {patient_block}

    {memory_block}

    Return ONLY valid JSON. Do not include explanations or extra text.
    """
    return full_prompt