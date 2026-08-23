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


# --- Tools Definitions ---
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


ALL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returnează ora actuală",
            "parameters": {"type": "object", "properties": {}, "required": []},
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
            "parameters": {"type": "object", "properties": {}, "required": []},
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

# Grupare pe categorii pentru injectare dinamică
TOOL_GROUPS = {
    "time": [t for t in ALL_TOOLS if t["function"]["name"] == "get_current_time"],
    "files": [
        t
        for t in ALL_TOOLS
        if t["function"]["name"] in ["list_files", "read_file", "write_file"]
    ],
    "memory": [
        t
        for t in ALL_TOOLS
        if t["function"]["name"] in ["read_memory", "write_memory"]
    ],
    "skills": [t for t in ALL_TOOLS if t["function"]["name"] == "load_skill"],
}


# --- Smart Router (Fără response_format incompatibil) ---
def choose_model_and_tools(task: str):
    router_prompt = """Ești un clasificator rapid de sarcini. Analizează cererea și răspunde EXCLUSIV cu un obiect JSON structurat astfel:
{
  "model": "fast" | "general" | "large",
  "tools": ["time", "files", "memory", "skills"]
}

Reguli clasificare model:
- "fast": Întrebări simple, definiții scurte (ex: "Ce este fotosinteza?"), saluturi, cereri de oră/timp.
- "general": Analize detaliate, explicații lungi, scriere sau debugging de cod.
- "large": Matematică avansată, algoritmi complecși, refactoring masiv.

Reguli unelte ("tools"):
- Trece doar categoriile de unelte strict necesare. Dacă nu este nevoie de nicio unealtă, pune lista goală [].

Exemple:
- "Ce este fotosinteza?": {"model": "fast", "tools": []}
- "Cât este ceasul?": {"model": "fast", "tools": ["time"]}
- "Ce ai salvat în memorie?": {"model": "general", "tools": ["memory"]}

Răspunde DOAR cu JSON-ul valid, fără alt text în jur."""

    try:
        response = client.chat.completions.create(
            model=MODELS["fast"],
            messages=[
                {"role": "system", "content": router_prompt},
                {"role": "user", "content": task},
            ],
            temperature=0.0,
        )

        raw_content = response.choices[0].message.content.strip()

        # Curățare în caz că modelul întoarce Markdown (```json ... ```)
        if raw_content.startswith("```"):
            raw_content = raw_content.split("```")[1]
            if raw_content.startswith("json"):
                raw_content = raw_content[4:]
        raw_content = raw_content.strip()

        data = json.loads(raw_content)

        model_key = data.get("model", "general").lower()
        selected_model = MODELS.get(model_key, MODELS["general"])
        selected_categories = data.get("tools", [])

        active_tools = []
        for cat in selected_categories:
            if cat in TOOL_GROUPS:
                active_tools.extend(TOOL_GROUPS[cat])

        tool_names = [t["function"]["name"] for t in active_tools]

        print(f"[Smart Router] Categorie detectată: '{model_key}'")
        print(f"[Smart Router] Model final ales: {selected_model}")
        print(
            f"[Smart Router] Tool-uri filtrate: {tool_names if tool_names else 'Niciunul (0 context irosit)'}\n"
        )

        return selected_model, active_tools

    except Exception as e:
        print(f"[Router Warning] Eroare parsare JSON / Fallback pe general: {e}\n")
        return MODELS["general"], ALL_TOOLS


def run_agent(user_message: str):
    model, active_tools = choose_model_and_tools(user_message)

    system_prompt = """Esti un agent AI cu memorie pe termen lung.
Folosește uneltele puse la dispoziție doar când este necesar.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    while True:
        kwargs = {
            "model": model,
            "messages": messages,
        }
        if active_tools:
            kwargs["tools"] = active_tools
            kwargs["tool_choice"] = "auto"

        response = client.chat.completions.create(**kwargs)

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
        user_message = "Ce este fotosinteza?"

    print(f"User query: '{user_message}'")
    print(run_agent(user_message))