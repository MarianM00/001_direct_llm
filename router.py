import json
import re
from openai import OpenAI

client = OpenAI(
    base_url="http://100.97.106.90:1234/v1",
    api_key="lm-studio",
)

ROUTER_MODEL = "google/gemma-4-e4b"

def route_intent(user_query: str) -> str:
    """Determină care este cel mai potrivit Agent Specializat (Rule-Based + LLM Fallback)."""
    query_lower = user_query.lower()

    # --- Step 1: Rule-based fast path (Reguli deterministice) ---
    system_keywords = ["fișiere", "fisiere", "director", "folder", "oră", "ora", "timp", "ceas", "listă", "lista"]
    coding_keywords = ["script", "cod", "python", "funcție", "functie", "bug", "eroare", "factorial", "execută", "executa", "calculează", "calculeaza"]
    
    # Verificare directă pentru sarcini clare de sistem
    if any(kw in query_lower for kw in system_keywords) and not any(kw in query_lower for kw in ["scrie script", "creează fișier", "creeaza fisier"]):
        print("[Router Rule] Potrivire pe reguli de sistem -> System Agent")
        return "system"

    # Verificare directă pentru cod
    if any(kw in query_lower for kw in coding_keywords) and any(verb in query_lower for verb in ["scrie", "creează", "creeaza", "modifică", "modifica", "rulează", "ruleaza"]):
        print("[Router Rule] Potrivire pe reguli de cod -> Coding Agent")
        return "coding"

    # --- Step 2: LLM Fallback (Dacă intenția este ambiguă) ---
    prompt = """Ești un clasificator de intenții ultra-strict.

Alege agentul potrivit pentru cererea utilizatorului:
- "system": dacă utilizatorul dorește să afle ora, să vadă/citească fișiere sau foldere de pe disc.
- "coding": dacă dorește scriere, modificare sau execuție de cod Python.
- "research": dacă dorește căutare/salvare în memorie, notițe sau explicații teoretice.

Răspunde EXCLUSIV cu un JSON valid:
{"agent": "system"}"""

    try:
        response = client.chat.completions.create(
            model=ROUTER_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.0,
            max_tokens=50
        )
        
        raw = response.choices[0].message.content.strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            agent_type = data.get("agent", "research").lower()
            if agent_type in ["coding", "research", "system"]:
                return agent_type
    except Exception as e:
        print(f"[Router Warning] Fallback la Research Agent: {e}")
    
    return "research"