from prompt_schemas import ResponsePlan, ParsedResponse

"""
Responsible for dictating the TONE of each response from the LLM
"""

def build_response_plan(parsed: ParsedResponse) -> ResponsePlan:
        plan = ResponsePlan()

        if parsed.intent == "venting":
            plan.tone = "empathetic"
            plan.goals = ["Validate feelings", "Encourage expression"]
            plan.constraints = ["Do not give advice"]

        elif parsed.intent == "question":
            plan.tone = "clear"
            plan.goals = ["Answer the question"]
            plan.constraints = ["Be concise"]

        elif parsed.intent == "worry":
            plan.tone = "reassuring"
            plan.goals = ["Acknowledge concern", "Reduce anxiety"]
            plan.constraints = ["Avoid alarmist language"]

        if parsed.emotion == "anxious":
            plan.constraints.append("Use grounding language")

        return plan

def default_response_plan() -> ResponsePlan:
    return ResponsePlan(
        tone="warm and professional",
        goals=["Establish rapport", "Invite the patient to share"],
        constraints=[
            "Do not make assumptions",
            "Ask at most one open-ended question"
        ]
    )