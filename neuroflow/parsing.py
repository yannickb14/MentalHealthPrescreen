from llm import LLMClient  # your LLM wrapper
from prompt_schemas import ParsedResponse
import prompts
from typing import Dict, List, Any, Optional
from memory import MemoryManager
import json
from tools import prompt_builder

#Send to API
async def post_patient_text_to_llm(llm_client: LLMClient, patient_text: str, thread_id, memory_context: str = ""):
    prompt = prompt_builder.build_full_prompt(patient_text, memory_context) #build prompt
    response = await llm_client.post_prompt(prompt, thread_id) #json response
    return response # dict[str->Any]

def parse_llm_response(raw_llm_response, input_text: str):
    """
    returnes a parsed version of the response returned by the llm, packed in a ParsedResponse object
    """
    #llm_response = raw_llm_response.replace("```json", "").replace("```", "").strip()
    llm_text = raw_llm_response["raw_text"]  # <-- use raw string
    llm_text = llm_text.replace("```json", "").replace("```", "").strip()

    data = json.loads(llm_text)

    parsed_response = ParsedResponse(
    input_text=input_text, #previous patient prompt
    intent=data["intent"],
    emotion=data["emotion"],
    response=data["response"],
    memory_candidates=data["memory_candidates"],
    entities=data.get("entities", {}),
    terminate=data.get("terminate", False)
    )

    return parsed_response


#POST
def post_to_memory(memory_manager: MemoryManager, thread_id: str, parsed_response):
    memory_candidates = parsed_response.memory_candidates
    memory_manager.write(thread_id, memory_candidates)





