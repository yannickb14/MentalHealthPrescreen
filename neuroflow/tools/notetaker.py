import os
import json
import re
from backboard import BackboardClient
from dotenv import load_dotenv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from datetime import datetime
from pathlib import Path

REPO_ROOT = "clinical_notes/" + Path(__file__).resolve().parents[2]

class NoteTaker:
    load_dotenv()

    api_key = os.getenv("BACKBOARD_API_KEY")  
    client = BackboardClient(api_key=api_key)

    @staticmethod
    def _notes_to_pdf(notes: dict, output_path: str):
        """
        Serialize SOAP notes into a readable PDF.
        """
        styles = getSampleStyleSheet()
        story = []

        def heading(text):
            story.append(Paragraph(f"<b>{text}</b>", styles["Heading2"]))
            story.append(Spacer(1, 0.2 * inch))

        def body(text):
            story.append(Paragraph(text or "N/A", styles["Normal"]))
            story.append(Spacer(1, 0.2 * inch))

        heading("Clinical SOAP Note")

        body(f"Patient ID: {notes.get('patient_id', 'unknown')}")
        body(f"Generated at: {datetime.utcnow().isoformat()} UTC")

        heading("Subjective")
        subj = notes.get("subjective", {})
        body(f"<b>Chief Complaint:</b> {subj.get('chief_complaint')}")
        body(f"<b>History of Present Illness:</b> {subj.get('history_of_present_illness')}")
        body(f"<b>Emotional State:</b> {subj.get('emotional_state')}")

        heading("Objective")
        obj = notes.get("objective", {})
        body(f"<b>Observations:</b> {obj.get('observations')}")
        body(f"<b>Risk Factors:</b> {', '.join(obj.get('risk_factors', []))}")

        heading("Assessment")
        assess = notes.get("assessment", {})
        body(f"<b>Summary:</b> {assess.get('summary')}")
        body(f"<b>Differential Diagnosis:</b> {', '.join(assess.get('differential_diagnosis', []))}")

        heading("Plan")
        plan = notes.get("plan", {})
        body(f"<b>Immediate Actions:</b> {plan.get('immediate_actions')}")
        body(f"<b>Recommendations:</b> {plan.get('recommendations')}")

        doc = SimpleDocTemplate(output_path, pagesize=LETTER)
        doc.build(story)

    @staticmethod
    async def generate_notes(thread_id: str, pdf_dir: str = REPO_ROOT):
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
        os.makedirs(pdf_dir, exist_ok=True)

        # 2. Send the command to Backboard
        # We treat this as a message, but the content forces the AI to step out of character.
        response = await NoteTaker.client.add_message(
            thread_id=thread_id,
            content=scribe_prompt,
            # If your Backboard plan supports 'json_object' response format, uncomment this:
            # response_format={"type": "json_object"} 
        )

        # 3. Extract and Clean the Output
        raw_content = response.content or response.message
        notes = NoteTaker._parse_json_safely(raw_content)
        if "error" in notes:
            return notes
        
        pdf_path = os.path.join(pdf_dir, f"{thread_id}_soap_note.pdf")
        NoteTaker._notes_to_pdf(notes, pdf_path)
    
        return {
            "notes": notes,
            "pdf_path": pdf_path
        }

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