import asyncio
from parsing import parse_prompt_llm
from memory import NeuroFlow
from llm import LLMClient
from models import ParsedPrompt

async def main():
    # ---- 1. Initialize LLM and memory ----
    llm = LLMClient()
    await llm.init_assistant()

    memory_manager = NeuroFlow()
    await memory_manager.init_assistant()

    # ---- 2. Create a session/thread for this patient ----
    thread = await memory_manager.client.create_thread(memory_manager.assistant.assistant_id)
    thread_id = thread.thread_id

    # ---- 3. Example patient input ----
    patient_input = "I have trouble sleeping at night and feel anxious about work."

    # ---- 4. Parse input with LLM ----
    parsed: ParsedPrompt = await parse_prompt_llm(patient_input, llm)

    print("Parsed Prompt:")
    print(parsed)

    # ---- 5. Write long-term memory only ----
    await memory_manager.write(thread_id, parsed.memory_candidates)

    # ---- 6. Generate a response (simplest case) ----
    response_prompt = f"Based on the patient input, respond empathetically:\n\n{patient_input}"
    reply = await llm.generate_response(prompt=response_prompt, thread_id=thread_id)

    print("\nNeuroFlow Reply:")
    print(reply)

if __name__ == "__main__":
    asyncio.run(main())
