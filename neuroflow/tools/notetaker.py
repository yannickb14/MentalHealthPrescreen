# Install: pip install backboard-sdk
import asyncio
import json
from backboard import BackboardClient
from ..prompt_schemas import ParsedResponse, ResponsePlan

from config import BACKBOARD_API_KEY

async def main():
    # Initialize the Backboard client
    client = BackboardClient(api_key=BACKBOARD_API_KEY)

    # Define a tool (function) for the assistant to call
    tools = [{
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        }
    }]

    # Create an assistant with the tool
    assistant = await client.create_assistant(
        name="Weather Assistant",
        tools=tools
    )

    # Create a thread
    thread = await client.create_thread(assistant.assistant_id)

    # Send a message that triggers the tool call
    response = await client.add_message(
        thread_id=thread.thread_id,
        content="What's the weather in San Francisco?",
        stream=False
    )

    # Check if the assistant requires action (tool call)
    if response.status == "REQUIRES_ACTION" and response.tool_calls:
        tool_outputs = []
        
        # Process each tool call
        for tc in response.tool_calls:
            if tc.function.name == "get_current_weather":
                # Get parsed arguments (required parameters are guaranteed by API)
                args = tc.function.parsed_arguments
                location = args["location"]
                
                # Execute your function and format the output
                weather_data = {
                    "temperature": "68°F",
                    "condition": "Sunny",
                    "location": location
                }
                
                tool_outputs.append({
                    "tool_call_id": tc.id,
                    "output": json.dumps(weather_data)
                })
        
        # Submit the tool outputs back to continue the conversation
        final_response = await client.submit_tool_outputs(
            thread_id=thread.thread_id,
            run_id=response.run_id,
            tool_outputs=tool_outputs
        )
        
        print(final_response.content)

async def generate_questions(
    self,
    parsed: ParsedResponse,
    long_term_memories: list[str] = None,
    plan: ResponsePlan = None,
    max_questions: int = 3
    ) -> list[str]:

    context_summary = f"Patient text: {parsed.text}\nIntent: {parsed.intent}\nEmotion: {parsed.emotion}\n"

    if long_term_memories:
        context_summary += "Previous patient information:\n"
        for mem in long_term_memories:
            context_summary += f"- {mem}\n"

    if plan:
        context_summary += f"Current plan goals: {plan.goals}\n"

    prompt = f"""
    You are a clinical AI assistant. Based on the patient input and previous patient information, generate up to {max_questions} concise follow-up questions
    that will help clarify the patient's state or gather clinically relevant information.
    Avoid questions the patient has already answered or facts already known.
    Return the questions as a JSON array of strings.
    {context_summary}
    """
    response_text = await self.llm.generate_response(prompt)
    import json
    try:
        questions = json.loads(response_text)
        if isinstance(questions, list):
            return questions
    except Exception:
        return [response_text.strip()]

    return []


if __name__ == "__main__":
    asyncio.run(main())
