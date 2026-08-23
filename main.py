from openai import OpenAI
from datetime import datetime
import os

client = OpenAI(
    base_url="http://192.168.100.2:1234/v1",
    api_key="lm-studio",
)

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def list_files(path="."):
    try:
        return "\n".join(os.listdir(path))
    except Exception as e:
        return f"Eroare: {e}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returnează ora actuală",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Listează fișierele dintr-un folder",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Calea folderului (implicit .)"
                    }
                },
                "required": []
            }
        }
    }
]

def run_agent(user_message: str):
    messages = [
        {
            "role": "system",
            "content": "Esti un agent AI. Foloseste tool-urile disponibile cand e nevoie."
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    while True:
        response = client.chat.completions.create(
            model="qwen/qwen3.5-9b",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = tool_call.function.arguments

            if name == "get_current_time":
                result = get_current_time()
            elif name == "list_files":
                import json
                path = json.loads(args).get("path", ".")
                result = list_files(path)
            else:
                result = "Tool necunoscut"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

if __name__ == "__main__":
    print(run_agent("Listează fișierele din folderul curent și spune-mi ora."))