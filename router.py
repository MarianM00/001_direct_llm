# router.py
from typing import Dict, Any

class ModelRouter:
    """Decide ce model și ce parametri să folosească pentru fiecare agent sau tip de sarcină."""
    
    # Configurația modelelor disponibile
    MODELS = {
        "fast": "google/gemma-4-e4b",
        "coder": "qwen/qwen3.5-9b",
    }

    @classmethod
    def get_route(cls, agent_type: str) -> Dict[str, Any]:
        """Returnează configurația optimă de model în funcție de agent."""
        if agent_type == "coding":
            return {
                "model": cls.MODELS["coder"],
                "temperature": 0.1,  # Temperatură mică pentru cod determinist
                "system_instruction": "Ești un Senior Python Engineer. Generezi DOAR cod valid și folosești tool-urile de fișiere/execuție."
            }
        elif agent_type == "system":
            return {
                "model": cls.MODELS["fast"],
                "temperature": 0.0,
                "system_instruction": "Ești un System Administrator. Execuți prompt comenzi de sistem și inspectezi directoare."
            }
        else:  # research / planner / memory
            return {
                "model": cls.MODELS["fast"],
                "temperature": 0.2,
                "system_instruction": "Ești un Research Assistant. Salvezi și extragi date precise din memorie."
            }