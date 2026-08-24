import os
import json
from datetime import datetime

MEMORY_FILE = "memory.md"
HISTORY_FILE = "history.json"

def read_memory(query=""):
    """Caută sau citește informații din memoria pe termen lung."""
    if not os.path.exists(MEMORY_FILE):
        return "Memoria este goală."
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if not query:
        return content

    lines = content.split("\n")
    relevant = [line for line in lines if any(word in line.lower() for word in query.lower().split())]
    if relevant:
        return "Contexte găsite în memorie:\n" + "\n".join(relevant)
    return f"Memorie citită complet:\n{content}"

def write_memory(content: str):
    """Salvează o informație importantă în memoria pe termen lung."""
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n- {datetime.now().strftime('%Y-%m-%d %H:%M')} | {content}")
    return f"Am salvat în memorie: '{content}'"

def load_history(limit=6):
    """Încarcă istoricul scurt al conversațiilor."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data[-limit:]
    except Exception:
        return []

def save_history(user_msg, agent_msg):
    """Salvează un schimb de mesaje în istoric."""
    history = load_history(limit=20)
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": agent_msg})
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-20:], f, indent=2, ensure_ascii=False)