from openai import OpenAI
from datetime import datetime
import os
import json

client = OpenAI(
    base_url="http://100.97.106.90:1234/v1",
    api_key="lm-studio",
)

# --- Tools existente ---
def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def list_files(path="."):
    try:
        return "\n".join(os.listdir(path))
    except Exception as e:
        return f"Eroare: {e}"

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Eroare: {e}"

def write_file(path, content):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Fișierul {path} a fost scris cu succes."
    except Exception as e:
        return f"Eroare: {e}"

def load_skill(name: str):
    path = f"skills/{name}.md"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Skill inexistent: {e}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returnează ora actuală",
            "parameters": {"type": "object", "properties": {}, "required": []}
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
                    "path": {"type": "string"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Citește un fișier text",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Scrie într-un fișier text",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "load_skill",
            "description": "Încarcă un skill complet după nume (ex: time, files, coding)",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Numele skill-ului fără .md"}
                },
                "required": ["name"]
            }
        }
    }
]

def run_agent(user_message: str):
    system_prompt = """Esti un agent AI.

Skill-uri disponibile:
- time → pentru ora
- files → pentru operații cu fișiere
- coding → pentru cod

Când ai nevoie de detalii despre un skill, apelează load_skill.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
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
            args = json.loads(tool_call.function.arguments or "{}")

            if name == "get_current_time":
                result = get_current_time()
            elif name == "list_files":
                result = list_files(args.get("path", "."))
            elif name == "read_file":
                result = read_file(args.get("path", ""))
            elif name == "write_file":
                result = write_file(args.get("path", ""), args.get("content", ""))
            elif name == "load_skill":
                result = load_skill(args.get("name", ""))
            else:
                result = "Tool necunoscut"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

if __name__ == "__main__":
    print(run_agent("Am nevoie de skill-ul de fișiere. Ce pot face cu el?"))