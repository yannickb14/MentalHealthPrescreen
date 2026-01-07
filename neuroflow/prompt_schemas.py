from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ParsedResponse:
    """
    Used by parsing.py to build a python object representing the JSON output of the llm, to be passed to memory and extracted.
    """
    text: str
    intent: str = None
    emotion: str = None
    memory_candidates: Dict[str, List[str]] = field(default_factory=lambda: {"short_term": [], "long_term": []})
    entities: Dict[str, str] = field(default_factory=dict)

@dataclass
class ResponsePlan:
    """
    Used by backbone to plan a response for the patient.
    unused so far.
    """
    tone: str = "neutral"  # e.g., empathetic, supportive
    goals: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    context: Dict = field(default_factory=dict)
