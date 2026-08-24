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
    prompt = f"""Ești un Planner expert pentru un sistem multi-agent.
Sarcina ta este să descompui cererea utilizatorului în pași logici executabili.

Agenți disponibili:
- "system": Poate rula `list_files` ȘI `get_current_time`. Dacă cererea cere fișiere SAU timpul/ora, folosește agentul system pentru ambele!
- "coding": Creează sau execută fișiere Python.
- "research": Salvează în memorie.

REGULI IMPORTANTE:
1. Dacă utilizatorul cere ceva legat de ORA și FIȘIERE, primul pas (system) trebuie să obțină ATÂT ora cât ȘI fișierele!
2. Dacă cererea este un salut ("Salut", "Ce faci", "Bună") sau o întrebare generală/conversațională:
   Returnează un singur pas pentru agentul "system" sau "research" care să răspundă scurt și politicos la conversație!

Format JSON de răspuns:
{{
  "steps": [
    {{"agent": "system", "task": "Obține lista fișierelor din director ȘI ora curentă din sistem."}},
    {{"agent": "coding", "task": "Creează scriptul gen_ora.py care scrie ora și fișierele obținute în ora.txt."}},
    {{"agent": "coding", "task": "Execută scriptul gen_ora.py."}},
    {{"agent": "research", "task": "Salvează în memorie generarea fișierului ora.txt."}}
  ]
}}

Cerere utilizator: "{user_query}"
Răspunde DOAR cu obiectul JSON:"""

    try:
        response = client.chat.completions.create(
            model=PLANNER_MODEL,
            messages=[
                {"role": "system", "content": "You output JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000
        )

        raw = response.choices[0].message.content.strip()

        print("\n--- [DEBUG] RĂSPUNS BRUT DE LA GEMMA ---")
        print(raw)
        print("------------------------------------------\n")

        raw_clean = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
        match = re.search(r"\{.*\}", raw_clean, re.DOTALL)
        if match:
            steps = json.loads(match.group(0)).get("steps", [])
            if not steps:
                print("⚠️ Obiectul JSON a fost găsit, dar cheia 'steps' este goală sau lipsesc pașii!")
            return steps
        else:
            print("⚠️ Regex-ul nu a găsit niciun obiect JSON între acolade {}!")

    except Exception as e:
        print(f"❌ [Planner Error]: {e}")
        
    return []