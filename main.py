from openai import OpenAI
from datetime import datetime
import json

client = OpenAI(
    base_url="http://192.168.100.2:1234/v1",
    api_key="lm-studio",
)

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returnează ora actuală a sistemului",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

messages = [
    {
        "role": "system",
        "content": "Esti un agent AI care poate folosi tool-uri. Cand ai nevoie de ora actuala, foloseste tool-ul get_current_time."
    },
    {
        "role": "user",
        "content": "Cat este ora actuala?"
    }
]

response = client.chat.completions.create(
    model="qwen/qwen3.5-9b",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

message = response.choices[0].message
messages.append(message)

if message.tool_calls:
    for tool_call in message.tool_calls:
        if tool_call.function.name == "get_current_time":
            result = get_current_time()
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

    final_response = client.chat.completions.create(
        model="qwen/qwen3.5-9b",
        messages=messages,
        tools=tools
    )
    print(final_response.choices[0].message.content)
else:
    print(message.content)