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
    """Descompune o cerere complexă într-un plan de execuție secvențial clar și robust."""
    
    prompt = f"""Ești un Planner/Orchestrator expert pentru un sistem multi-agent.
Sarcina ta este să analizezi cererea utilizatorului și să o descompui în pași logici secvențiali.

Agenți disponibili:
- "system": Inspectează fișiere/directoare sau obține ora curentă.
- "coding": Creează, editează, refactorizează SAU execută cod Python.
- "research": Caută în memorie sau salvează note/informații în memoria pe termen lung.

Reguli de planificare:
1. Dacă cererea implică scrierea și executarea unui script, SEPARĂ procesul în doi pași 'coding':
   - Pasul A: Creează scriptul Python.
   - Pasul B: Execută scriptul Python creat.
2. Păstrează sarcinile simple și directe.
3. Răspunde EXCLUSIV cu un obiect JSON valid.

Exemplu format răspuns:
{{
  "steps": [
    {{"agent": "system", "task": "Află lista fișierelor și ora curentă."}},
    {{"agent": "coding", "task": "Creează scriptul gen_ora.py."}},
    {{"agent": "coding", "task": "Execută scriptul gen_ora.py."}},
    {{"agent": "research", "task": "Salvează în memorie faptul că gen_ora.py a fost creat și executat."}}
  ]
}}

Cererea utilizatorului: "{user_query}"

Răspunde DOAR cu obiectul JSON:"""

    try:
        response = client.chat.completions.create(
            model=PLANNER_MODEL,
            messages=[
                {"role": "system", "content": "You output JSON only. Keep steps clear and modular."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000
        )

        raw = response.choices[0].message.content.strip()
        raw_clean = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
        
        match = re.search(r"\{.*\}", raw_clean, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            return data.get("steps", [])
        else:
            print(f"⚠️ [Planner Debug] Nu s-a găsit JSON valid în răspuns:\n{raw}")
            
    except Exception as e:
        print(f"❌ [Planner Error]: {e}")
    
    return []