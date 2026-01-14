INTENT_DEFINITIONS = """
Intent Definitions for NeuroFlow:

venting:
    Expression of emotions, frustrations, or stress about personal experiences or situations.
    Focus is on emotional release rather than facts or actionable requests.
    Example: "I’m so overwhelmed with work today."

question:
    An inquiry directed to the therapist/AI, seeking advice, guidance, or information.
    Example: "How can I manage my anxiety at night?"

report:
    A factual statement about the patient’s life, health, or circumstances.
    Often objective and meant to convey information.
    Example: "I have trouble sleeping more than 4 hours a night."

reflection:
    Insightful observations about self, patterns, or behavior.
    Shows awareness or contemplation of thoughts and feelings.
    Example: "I notice I get anxious whenever I procrastinate."

goal:
    Statements expressing intentions, targets, or desired changes in behavior or life.
    Example: "I want to start meditating every morning."

narrative:
    Storytelling or recounting past experiences, often giving context to current feelings.
    Example: "Last week, I had an argument with my friend, and it left me feeling down."

worry:
    Repetitive thoughts or anxious rumination about potential negative outcomes.
    Example: "I keep thinking I’ll fail at my presentation."

other:
    Anything that doesn’t clearly fit into the above categories.
    Can include neutral statements, random thoughts, or ambiguous input.
"""

EMOTION_DEFINITIONS = """
anxious:
    Patient feels worried, tense, nervous, or uneasy about current or future situations.
    Example: "I feel nervous about tomorrow's presentation."

sad:
    Patient feels down, low mood, disappointment, or general unhappiness.
    Example: "I’ve been feeling sad and unmotivated all week."

happy:
    Patient expresses joy, contentment, or positive feelings.
    Example: "I felt really happy spending time with my friends today."

neutral:
    Patient expresses facts, observations, or emotions that are calm, indifferent, or stable.
    Example: "I went to work today and completed my tasks."

angry:
    Patient feels frustration, irritation, or resentment.
    Example: "I’m so frustrated with how my manager handled that situation."

guilty:
    Patient feels remorse, regret, or responsibility for perceived mistakes or harm.
    Example: "I feel guilty for forgetting my friend’s birthday."

hopeful:
    Patient expresses optimism or positive anticipation about future events or changes.
    Example: "I’m hopeful that therapy will help me manage my anxiety."

fearful:
    Patient feels afraid, threatened, or unsafe.
    Example: "I’m scared something bad is going to happen."

overwhelmed:
    Patient feels unable to cope due to emotional, mental, or situational overload.
    Example: "There’s too much going on and I can’t keep up."

lonely:
    Patient feels isolated, disconnected, or lacking meaningful social connection.
    Example: "I feel alone even when I’m around other people."

ashamed:
    Patient feels embarrassment or negative self-judgment related to identity or behavior.
    Example: "I feel ashamed of how I acted."

relieved:
    Patient feels release from stress, worry, or pressure after a resolution.
    Example: "I feel relieved now that the exam is over."

confused:
    Patient feels uncertain, unclear, or mentally disoriented.
    Example: "I don’t know what I’m supposed to feel or do."

frustrated:
    Patient feels blocked, stuck, or thwarted in efforts or goals.
    Example: "No matter what I try, nothing seems to work."

numb:
    Patient feels emotionally blunted, detached, or empty.
    Example: "I don’t really feel anything right now."

grateful:
    Patient expresses appreciation or thankfulness.
    Example: "I’m really grateful for the support I’ve been getting."

motivated:
    Patient feels driven or energized toward goals or action.
    Example: "I finally feel motivated to make some changes."

hopeless:
    Patient feels pessimistic, helpless, or lacking expectation of improvement.
    Example: "It feels like nothing is ever going to get better."

resentful:
    Patient feels lingering anger or bitterness about past events or treatment.
    Example: "I still feel resentful about how I was treated."

calm:
    Patient feels relaxed, steady, or at ease.
    Example: "I feel calm and more grounded today."

self-critical:
    Patient expresses harsh judgment or dissatisfaction toward themselves.
    Example: "I’m really hard on myself for every mistake."

trusting:
    Patient feels safe, open, or confident in others or a process.
    Example: "I trust that this will work out."

disappointed:
    Patient feels let down due to unmet expectations.
    Example: "I’m disappointed with how things turned out."
"""


RESPONSE_INSTRUCTIONS = """
You are a licensed clinical nurse interacting with a patient in a healthcare setting.
Respond in a calm, respectful, and nonjudgmental manner using clear, plain language.
Explain medical terms when needed and avoid unnecessary jargon.

Maintain professional boundaries at all times.
Do not reference internal systems, prompts, or technical processes.
Accurately reflect the patient’s concerns and acknowledge emotions without validating harmful beliefs or minimizing symptoms.

Ask focused, clinically relevant follow-up questions, one or two at a time.
Prefer open-ended questions unless specific clarification is required.
Listen carefully and respond directly to what the patient is expressing.

Provide evidence-based information aligned with standard nursing practice.
Frame guidance as options rather than commands.
Encourage patient autonomy and shared decision-making.
Do not make diagnoses unless explicitly instructed and clinically appropriate.

When a patient appears distressed, acknowledge their emotional state before problem-solving.
Use supportive, grounding language without offering false reassurance.
Remain steady, empathetic, and composed.

When safety or risk concerns arise, address them calmly and directly.
Prioritize patient safety and ask sensitively about risk when indicated.
Encourage appropriate escalation to higher levels of care when necessary.
Do not provide instructions that could enable harm.

Offer realistic reassurance grounded in facts rather than guarantees.
Conclude each response with a brief summary of key points.
Outline clear next steps and invite the patient to share additional questions or concerns.
Adhere to professional, ethical, and clinical standards at all times.
"""