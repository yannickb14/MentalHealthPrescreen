import os
import json
import re
from backboard import BackboardClient

class NoteTaker:
    api_key = os.getenv("BACKBOARD_API_KEY")  
    client = BackboardClient(api_key=api_key)

    @staticmethod
    async def generate_notes(thread_id: str):
        """
        Interacts with the EXISTING thread and memory to generate a clinical summary.
        It does not continue the conversation; it forces a 'Scribe' mode response.
        """
        
        # 1. Define the System Instruction for the Scribe
        # We start with [SYSTEM] to tell Backboard this isn't the patient talking.
        scribe_prompt = """
        [SYSTEM INSTRUCTION: END OF CLINICAL SESSION]
        
        You are now acting as a Medical Scribe. 
        Review the entire conversation history and the long-term memories you have stored for this patient.
        
        Generate a comprehensive SOAP Note in strictly valid JSON format.
        
        The JSON must follow this structure exactly:
        {
            "patient_id": "derived_from_context_or_unknown",
            "subjective": {
                "chief_complaint": "Main issue reported by patient",
                "history_of_present_illness": "Summary of symptoms, duration, and context",
                "emotional_state": "Observed mood (e.g., anxious, flat, elevated)"
            },
            "objective": {
                "observations": "Factual observations from the session",
                "risk_factors": ["List", "of", "detected", "risks"]
            },
            "assessment": {
                "summary": "Clinical impression of the patient's status",
                "differential_diagnosis": ["Potential", "Diagnoses"]
            },
            "plan": {
                "immediate_actions": "Steps to take right now",
                "recommendations": "Therapeutic suggestions for next time"
            }
        }
        
        Do not include markdown formatting (like ```json). Output raw JSON only.
        """

        print(f"📝 Requesting Clinical Notes for Thread: {thread_id}...")

        # 2. Send the command to Backboard
        # We treat this as a message, but the content forces the AI to step out of character.
        response = await NoteTaker.client.add_message(
            thread_id=thread_id,
            content=scribe_prompt,
            # If your Backboard plan supports 'json_object' response format, uncomment this:
            # response_format={"type": "json_object"} 
        )

        # 3. Extract and Clean the Output
        raw_content = response.latest_message.content
        return NoteTaker._parse_json_safely(raw_content)

    @staticmethod
    def _parse_json_safely(text: str):
        """
        LLMs often wrap JSON in markdown (```json ... ```). This strips it.
        """
        try:
            # Remove markdown code blocks if present
            clean_text = re.sub(r"```json\s*", "", text)
            clean_text = re.sub(r"```\s*", "", clean_text)
            clean_text = clean_text.strip()
            
            return json.loads(clean_text)
        except json.JSONDecodeError:
            print(f"❌ JSON Parsing Failed. Raw output: {text}")
            # Fallback: Return the raw text wrapped in a dict so the app doesn't crash
            return {
                "error": "Failed to parse JSON", 
                "raw_text": text
            }

# --- usage example ---
# taker = NoteTaker()
# notes = await taker.generate_notes(thread_id="thread_abc123")
# print(notes['assessment']['summary'])