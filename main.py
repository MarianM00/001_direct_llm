import json
import os
import re
import subprocess
import sys
from datetime import datetime
from openai import OpenAI

client = OpenAI(
    base_url="http://100.97.106.90:1234/v1",
    api_key="lm-studio",
)

HISTORY_FILE = "history.json"
MEMORY_FILE = "memory.md"
MAX_STEPS = 6


# --- Managementul Memoriei pe Termen Scurt (History) ---
def load_history(limit=6):
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data[-limit:]
    except Exception:
        return []


def save_history(user_msg, agent_msg):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": agent_msg})

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-20:], f, indent=2, ensure_ascii=False)


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
        return f"Fișierul '{path}' a fost scris cu succes."
    except Exception as e:
        return f"Eroare la scriere: {e}"


def execute_python(path: str):
    """Execută un fișier Python și returnează STDOUT sau STDERR pentru autocorecție."""
    if not os.path.exists(path):
        return f"Eroare: Fișierul '{path}' nu există."
    try:
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return f"✅ Execuție cu succes!\nOutput:\n{result.stdout if result.stdout else '(fără output)'}"
        else:
            return f"❌ Eroare la execuție (Code {result.returncode}):\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "❌ Eroare: Scriptul a depășit timpul maxim de execuție (Timeout 10s)."
    except Exception as e:
        return f"❌ Eroare neașteptată la execuție: {e}"


def load_skill(name: str):
    path = f"skills/{name}.md"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Skill inexistent: {e}"


def read_memory(query=""):
    if not os.path.exists(MEMORY_FILE):
        return "Memoria este goală."
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if not query:
        return content

    lines = content.split("\n")
    relevant = [
        line
        for line in lines
        if any(word in line.lower() for word in query.lower().split())
    ]
    if relevant:
        return "Contexte găsite în memorie:\n" + "\n".join(relevant)
    return f"Memorie citită complet:\n{content}"


def write_memory(content: str):
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n- {datetime.now().strftime('%Y-%m-%d %H:%M')} | {content}")
    return f"Am salvat în memorie: '{content}'"


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
            "description": "Listează fișierele din director",
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
            "description": "Scrie conținut într-un fișier",
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
            "name": "execute_python",
            "description": "Execută un fișier script Python local și verifică dacă funcționează fără erori.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Calea către fișierul .py de executat",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "load_skill",
            "description": "Încarcă un skill specific",
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
            "description": "Caută sau citește informații din memoria pe termen lung",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Cuvinte cheie de căutat",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_memory",
            "description": "Salvează o informație importantă în memorie pe termen lung",
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

TOOL_GROUPS = {
    "time": [t for t in ALL_TOOLS if t["function"]["name"] == "get_current_time"],
    "files": [
        t
        for t in ALL_TOOLS
        if t["function"]["name"]
        in ["list_files", "read_file", "write_file", "execute_python"]
    ],
    "memory": [
        t
        for t in ALL_TOOLS
        if t["function"]["name"] in ["read_memory", "write_memory"]
    ],
    "skills": [t for t in ALL_TOOLS if t["function"]["name"] == "load_skill"],
}

MODELS = {
    "fast": "google/gemma-4-e4b",
    "general": "qwen/qwen3.5-9b",
    "large": "google/gemma-4-12b-qat",
}


# --- Smart Router (Versiune Îmbunătățită și Robustă) ---
def choose_model_and_tools(task: str):
    router_prompt = """Ești un clasificator rapid de sarcini. Analizează cererea și răspunde EXCLUSIV cu un obiect JSON în următorul format:
{
  "model": "fast",
  "tools": ["time"]
}

Opțiuni valide pentru "model": "fast", "general", "large"
Opțiuni valide pentru "tools": "time", "files", "memory", "skills"

Reguli clasificare model:
- "fast": Întrebări simple, conversație generală, explicații teoretice (ex: fotosinteză), oră/timp, salvare/citire simplă din memorie.
- "general": Analize detaliate, manipulare fișiere, scriere, rulare sau debugging de cod Python.
- "large": Matematică avansată, algoritmi complecși, refactoring masiv.

Reguli unelte ("tools"):
- Dacă cererea este teoretică sau generală (ex: "Explică fotosinteza"), lista "tools" va fi goliți: [].
- Dacă cererea cere citirea/salvarea memoriei, adaugă "memory".
- Dacă cererea cere scriere sau rulare de cod, adaugă "files".

FOARTE IMPORTANT: Răspunde DOAR cu obiectul JSON raw. Nu adăuga text înainte sau după."""

    try:
        response = client.chat.completions.create(
            model=MODELS["fast"],
            messages=[
                {"role": "system", "content": router_prompt},
                {"role": "user", "content": task},
            ],
            temperature=0.0,
            max_tokens=150,
        )

        raw_content = response.choices[0].message.content.strip()

        # Extrage cu RegEx exact obiectul JSON dintre { și }
        match = re.search(r"\{.*\}", raw_content, re.DOTALL)
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)
        else:
            raise ValueError(f"Nu s-a găsit un JSON valid în răspuns: {raw_content}")

        model_key = data.get("model", "general").lower()
        selected_model = MODELS.get(model_key, MODELS["general"])
        selected_categories = data.get("tools", [])

        active_tools = []
        for cat in selected_categories:
            if cat in TOOL_GROUPS:
                active_tools.extend(TOOL_GROUPS[cat])

        tool_names = [t["function"]["name"] for t in active_tools]

        print(f"[Smart Router] Categorie: '{model_key}' | Model: {selected_model}")
        print(
            f"[Smart Router] Tool-uri active: {tool_names if tool_names else 'Niciunul'}\n"
        )

        return selected_model, active_tools

    except Exception as e:
        print(f"[Router Warning] Fallback pe general: {e}\n")
        return MODELS["general"], ALL_TOOLS


# --- ReAct Execution Engine + Self-Correction Loop ---
def run_agent(user_message: str):
    model, active_tools = choose_model_and_tools(user_message)
    short_term_history = load_history(limit=4)

    system_prompt = """Ești un agent autonom bazat pe ReAct (Reasoning + Acting) cu autocorecție.
Când scrii sau editezi scripturi Python:
1. Scrie codul în fișier folosind 'write_file'.
2. Execută ÎNTOTDEAUNA fișierul folosind 'execute_python' pentru a valida că funcționează.
3. Dacă întâmpini erori la execuție, citește erorile, înțelege ce s-a întâmplat, scrie varianta corectată și execută din nou (Auto-Correction).
4. Oferă răspunsul final doar când codul a fost testat și funcționează cu succes.

Fii concis și direct."""

    messages = [{"role": "system", "content": system_prompt}]
    if short_term_history:
        messages.extend(short_term_history)

    messages.append({"role": "user", "content": user_message})

    step = 1
    final_answer = ""

    while step <= MAX_STEPS:
        print(f"--- [Pasul {step}/{MAX_STEPS}] ---")

        kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": 700,
        }
        if active_tools:
            kwargs["tools"] = active_tools
            kwargs["tool_choice"] = "auto"

        response = client.chat.completions.create(**kwargs)
        message = response.choices[0].message
        messages.append(message)

        if message.tool_calls:
            if message.content:
                print(f"🧠 [Thought]: {message.content}")

            for tool_call in message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments or "{}")

                print(f"⚙️ [Action]: Apelează '{name}' cu argumentele: {args}")

                if name == "get_current_time":
                    result = get_current_time()
                elif name == "list_files":
                    result = list_files(args.get("path", "."))
                elif name == "read_file":
                    result = read_file(args.get("path", ""))
                elif name == "write_file":
                    result = write_file(
                        args.get("path", ""), args.get("content", "")
                    )
                elif name == "execute_python":
                    result = execute_python(args.get("path", ""))
                elif name == "load_skill":
                    result = load_skill(args.get("name", ""))
                elif name == "read_memory":
                    result = read_memory(args.get("query", ""))
                elif name == "write_memory":
                    result = write_memory(args.get("content", ""))
                else:
                    result = "Tool necunoscut"

                print(f"👁️ [Observation]: {result}\n")

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),
                    }
                )
            step += 1
        else:
            print("🏁 [Final Answer]:")
            final_answer = message.content or "Sarcina a fost finalizată."
            save_history(user_message, final_answer)
            return final_answer

    final_answer = "❌ S-a atins limita maximă de pași fără un răspuns final."
    save_history(user_message, final_answer)
    return final_answer


if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_message = " ".join(sys.argv[1:])
    else:
        user_message = "Creează un fișier test.py care să calculeze al 10-lea număr Fibonacci și să-l afișeze, apoi execută-l."

    print(f"User query: '{user_message}'\n")
    print(run_agent(user_message))