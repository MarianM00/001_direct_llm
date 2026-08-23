from openai import OpenAI
from datetime import datetime
import os
import json

client = OpenAI(
    base_url="http://100.97.106.90:1234/v1",
    api_key="lm-studio",
)

MEMORY_FILE = "memory.md"

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
        return f"Fișierul {path} a fost scris."
    except Exception as e:
        return f"Eroare: {e}"

def load_skill(name: str):
    path = f"skills/{name}.md"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Skill inexistent: {e}"

def read_memory():
    if not os.path.exists(MEMORY_FILE):
        return "Memoria este goală."
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return f.read()

def write_memory(content: str):
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n- {datetime.now().strftime('%Y-%m-%d %H:%M')} | {content}")
    return "Memorie actualizată."

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
            "description": "Listează fișierele",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Citește un fișier",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Scrie un fișier",
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
            "description": "Încarcă un skill (time, files, coding)",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_memory",
            "description": "Citește memoria pe termen lung",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_memory",
            "description": "Salvează o informație importantă în memorie",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Informația de salvat"}
                },
                "required": ["content"]
            }
        }
    }
]

def run_agent(user_message: str):
    system_prompt = """Esti un agent AI cu memorie pe termen lung.

Skill-uri: time, files, coding.
Folosește load_skill când ai nevoie de detalii.
Folosește read_memory / write_memory pentru informații persistente.
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
            elif name == "read_memory":
                result = read_memory()
            elif name == "write_memory":
                result = write_memory(args.get("content", ""))
            else:
                result = "Tool necunoscut"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

if __name__ == "__main__":
    print(run_agent("Ce știi despre proiectul meu? Citește memoria, nu mai scrie iar in fisier."))