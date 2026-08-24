# planner.py
import json
import re
from typing import List, Dict
from openai import OpenAI

client = OpenAI(
    base_url="http://100.97.106.90:1234/v1",
    api_key="lm-studio",
)

PLANNER_MODEL = "google/gemma-4-e4b"

def create_plan(user_query: str) -> List[Dict[str, str]]:
    """Descompune o cerere complexă într-un plan de execuție secvențial pentru agenți."""
    
    prompt = f"""Ești un Planner/Orchestrator expert pentru un sistem multi-agent.
Sarcina ta este să analizezi cererea utilizatorului și să o descompui într-o serie de pași logici secvențiali.

Agenți disponibili:
- "system": Pentru inspectat fișiere, directoare sau aflarea orei curente.
- "coding": Pentru creare, editare, refactoring și execuție de cod Python.
- "research": Pentru căutare în memorie sau salvarea preferințelor/notițelor în memorie.

Reguli:
1. Răspunde EXCLUSIV cu un obiect JSON valid într-o singură linie sau pe un singur rand pentru fiecare proprietate string.
2. Descrierea "task" trebuie să fie scurtă și concisă (sub 15 cuvinte).

Exemplu format raspuns:
{{
  "steps": [
    {{"agent": "system", "task": "Află fișierele din director și ora curentă."}},
    {{"agent": "coding", "task": "Scrie și execută scriptul gen_info.py pentru a crea info.txt."}},
    {{"agent": "research", "task": "Salvează în memorie faptul că info.txt a fost creat."}}
  ]
}}

Cererea utilizatorului: "{user_query}"

Răspunde DOAR cu obiectul JSON:"""

    try:
        response = client.chat.completions.create(
            model=PLANNER_MODEL,
            messages=[
                {"role": "system", "content": "You output valid JSON only. Keep string values concise and on a single line."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000  # Mărit pentru a evita tăierea răspunsului
        )

        raw = response.choices[0].message.content.strip()
        
        # Curățăm blocuri de markdown ```json ... ```
        raw_clean = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
        
        # Înlocuim liniile noi reale din interiorul răspunsului pentru a nu bloca json.loads
        # (înlocuiește no-line breaks stricați dacă există)
        match = re.search(r"\{.*\}", raw_clean, re.DOTALL)
        if match:
            json_str = match.group(0)
            # Încercăm să parsăm JSON-ul
            data = json.loads(json_str)
            return data.get("steps", [])
        else:
            print(f"⚠️ [Planner Debug] Nu s-a găsit JSON în răspuns. Răspuns brut:\n{raw}")
            
    except Exception as e:
        print(f"❌ [Planner Error]: {e}")
        if 'raw' in locals():
            print(f"⚠️ Răspunsul brut a fost:\n{raw}")
    
    return []