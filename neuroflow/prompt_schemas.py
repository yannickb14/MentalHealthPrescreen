from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ParsedResponse:
    """
    Used by parsing.py to build a python object representing the JSON output of the llm, to be passed to memory and extracted.
    """
    input_text: str
    intent: str = None
    emotion: str = None
    response: str = None #follow up from llm
    memory_candidates: Dict[str, List[str]] = field(default_factory=lambda: {"short_term": [], "long_term": []})
    entities: Dict[str, str] = field(default_factory=dict)
    terminate: bool = False

@dataclass
class ResponsePlan:
    """
    Used by backbone to plan a response for the patient.
    Depending on the patient's intent and emotion, the llm should respond accordingly.

    WILL USE INTENT AND EMOTION TO RESPOND ACCORDINGLY
    """
    tone: str = "neutral"  # e.g., empathetic, supportive
    goals: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    context: Dict = field(default_factory=dict)

    

