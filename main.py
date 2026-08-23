import json
import os
import sys
from datetime import datetime
from openai import OpenAI

client = OpenAI(
    base_url="http://100.97.106.90:1234/v1",
    api_key="lm-studio",
)

MEMORY_FILE = "memory.md"

MODELS = {
    "fast": "google/gemma-4-e4b",
    "general": "qwen/qwen3.5-9b",
    "large": "google/gemma-4-12b-qat",
}


# --- Model Router Inteligent (LLM-based) ---
def choose_model(task: str) -> str:
    router_prompt = """Ești un router de sarcini AI. Analizează mesajul utilizatorului și clasifică-l într-una din categorii:
- "fast": Întrebări simple, saluturi, cereri rapide de timp, liste scurte.
- "general": Explicații, analize, scriere de cod, reasoning, întrebări structurate.
- "large": Task-uri matematice complexe, refactoring masiv de cod, logică grea.

Răspunde STRICT cu un singur cuvânt: fast, general, sau large."""

    try:
        response = client.chat.completions.create(
            model=MODELS["fast"],
            messages=[
                {"role": "system", "content": router_prompt},
                {"role": "user", "content": task},
            ],
            temperature=0.0,
        )

        category = response.choices[0].message.content.strip().lower()

        for key in MODELS.keys():
            if key in category:
                return MODELS[key]

    except Exception as e:
        print(f"[Router Warning] Fallback pe general: {e}")

    return MODELS["general"]


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
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Listează fișierele",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Citește un fișier",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
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
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "load_skill",
            "description": "Încarcă un skill (time, files, coding)",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_memory",
            "description": "Citește memoria pe termen lung",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_memory",
            "description": "Salvează o informație importantă în memorie",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Informația de salvat",
                    }
                },
                "required": ["content"],
            },
        },
    },
]


def run_agent(user_message: str):
    model = choose_model(user_message)
    print(f"[Smart Router] Model ales de LLM: {model}\n")

    system_prompt = """Esti un agent AI cu memorie pe termen lung.

Skill-uri: time, files, coding.
Folosește load_skill când ai nevoie de detalii.
Folosește read_memory / write_memory pentru informații persistente.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    while True:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
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
                result = write_file(
                    args.get("path", ""),
                    args.get("content", ""),
                )
            elif name == "load_skill":
                result = load_skill(args.get("name", ""))
            elif name == "read_memory":
                result = read_memory()
            elif name == "write_memory":
                result = write_memory(args.get("content", ""))
            else:
                result = "Tool necunoscut"

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
            )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_message = " ".join(sys.argv[1:])
    else:
        user_message = "Cât este ceasul acum?"

    print(f"User query: '{user_message}'")
    print(run_agent(user_message))