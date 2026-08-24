# context_manager.py
from typing import Dict, Any

class ContextManager:
    """Gestionează, filtrează și formatează contextul transmis între agenți."""
    
    @staticmethod
    def format_context_for_agent(step_results: Dict[str, Any], max_tokens_approx: int = 1500) -> str:
        """Sintetizează rezultatele anteriorilor pași într-un format structurat și curat."""
        if not step_results:
            return ""

        context_lines = ["\n--- 📥 CONTEXT DIN PAȘII ANTERIORI (DATE REALE OBȚINUTE) ---"]
        
        for step_name, result in step_results.items():
            result_str = str(result).strip()
            
            # Curățăm zgomotul inutil dacă rezultatul e prea lung
            if len(result_str) > max_tokens_approx:
                result_str = result_str[:max_tokens_approx] + "\n...[date trunchiate pentru economie de context]..."

            context_lines.append(f"📌 [{step_name.upper()}]:\n{result_str}\n")
            
        context_lines.append("---------------------------------------------------\n")
        return "\n".join(context_lines)

    @staticmethod
    def build_actionable_prompt(task: str, context: str) -> str:
        """Construiește un prompt ultra-strict care forțează LLM-ul să genereze un apel de tool."""
        return f"""SARCINA TA CURENTĂ:
{task}

{context}
⚠️ REGULĂ STRICTĂ DE EXECUȚIE:
- NU oferi un răspuns final doar din text!
- Pentru a îndeplini această sarcină, EȘTI OBLIGAT să apelezi un TOOL la acest pas.
- Dacă trebuie să creezi scriptul `gen_ora.py`, apelează `write_file` cu codul Python complet ce scrie ora și fișierele din context în `ora.txt`.
- Dacă trebuie să executat scriptul, apelează `execute_python`.

Apelează Tool-ul corespunzător acum:"""