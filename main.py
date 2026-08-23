from openai import OpenAI
from datetime import datetime
import os
import json

client = OpenAI(
    base_url="http://100.97.106.90:1234/v1",  # ← IP-ul Tailscale + portul 1234
    api_key="lm-studio",
)

# --- Tools ---
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
                    "path": {"type": "string", "description": "Calea folderului"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Citește conținutul unui fișier text",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Calea fișierului"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Scrie conținut într-un fișier text",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Calea fișierului"},
                    "content": {"type": "string", "description": "Conținutul de scris"}
                },
                "required": ["path", "content"]
            }
        }
    }
]

# --- Încarcă skill-urile ---
def load_skills():
    skills_dir = "skills"
    if not os.path.exists(skills_dir):
        return ""
    
    content = []
    for filename in os.listdir(skills_dir):
        if filename.endswith(".md"):
            with open(os.path.join(skills_dir, filename), "r", encoding="utf-8") as f:
                content.append(f"### Skill: {filename}\n{f.read()}")
    return "\n\n".join(content)

def run_agent(user_message: str):
    skills = load_skills()
    
    system_prompt = f"""Esti un agent AI.
Foloseste tool-urile cand e nevoie.

{skills}
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
            else:
                result = "Tool necunoscut"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

if __name__ == "__main__":
    print(run_agent("Ce skill-uri ai disponibile?"))