# workflow_engine.py
from dataclasses import dataclass, field
from typing import Dict, Any, List

from agents.system_agent import SystemAgent
from agents.coding_agent import CodingAgent
from agents.research_agent import ResearchAgent
from context_manager import ContextManager


@dataclass
class WorkflowState:
    """Starea partajată transmisă de la un agent la altul."""
    user_goal: str
    step_results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class SequentialWorkflowEngine:
    """Orchestrator secvențial cu mecanism automat de Error Recovery & Self-Correction."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.agent_registry = {
            "system": SystemAgent(),
            "coding": CodingAgent(),
            "research": ResearchAgent()
        }

    def _execute_agent(self, agent_instance, prompt: str):
        if hasattr(agent_instance, "run"):
            return agent_instance.run(prompt)
        elif hasattr(agent_instance, "execute"):
            return agent_instance.execute(prompt)
        elif callable(agent_instance):
            return agent_instance(prompt)
        else:
            raise AttributeError(f"Agentul {type(agent_instance).__name__} nu are o metodă validă de execuție.")

    def _is_error_output(self, result: Any) -> bool:
        """Detectează dacă rezultatul conține un crash real (Traceback/Excepție nesemnalată)."""
        res_str = str(result)
        # Căutăm DOAR indicatoarele reale de crash din terminal:
        critical_errors = [
            "Traceback (most recent call last):",
            "❌ Eroare la execuție",
            "SyntaxError:",
            "IndentationError:"
        ]
        return any(keyword in res_str for keyword in critical_errors)

    def run_pipeline(self, steps: List[Dict[str, str]], user_goal: str) -> WorkflowState:
        state = WorkflowState(user_goal=user_goal)
        print(f"\n🚀 [Workflow Engine] Start Pipeline cu Self-Correction activat pentru: '{user_goal}'\n" + "="*70)

        for i, step in enumerate(steps, 1):
            agent_type = step["agent"]
            specific_task = step["task"]
            step_name = f"Pasul_{i}_{agent_type}"

            print(f"\n🔄 [Workflow Step {i}/{len(steps)}] -> Agent: [{agent_type.upper()}]")
            print(f"🎯 Sarcina: {specific_task}")

            if agent_type not in self.agent_registry:
                error_msg = f"Agentul '{agent_type}' nu este înregistrat!"
                state.errors.append(error_msg)
                print(f"❌ {error_msg}")
                break

            agent = self.agent_registry[agent_type]
            success = False
            last_error_context = ""

            # Bucla de Error Recovery & Self-Correction
            for attempt in range(1, self.max_retries + 1):
                if attempt > 1:
                    print(f"\n🔄 [SELF-CORRECTION] Încercarea {attempt}/{self.max_retries} pentru {step_name}...")

                # 1. Obținem contextul structurat
                formatted_context = ContextManager.format_context_for_agent(state.step_results)
                
                # 2. Adăugăm eroarea anterioară în prompt dacă suntem în re-încercare
                if last_error_context:
                    formatted_context += f"\n⚠️ [EROARE LA ÎNCERCAREA ANTERIOARĂ]:\n{last_error_context}\n"
                    task_with_correction = f"{specific_task} (Corectează eroarea apărută anterior!)"
                else:
                    task_with_correction = specific_task

                # 3. Construim prompt-ul final
                combined_prompt = ContextManager.build_actionable_prompt(task_with_correction, formatted_context)

                try:
                    result = self._execute_agent(agent, combined_prompt)

                    # Verificăm dacă execuția a întors o eroare de Python/Sistem
                    if self._is_error_output(result):
                        print(f"⚠️ [Workflow Engine] S-a detectat o eroare în output la încercarea {attempt}!")
                        last_error_context = str(result)
                    else:
                        state.step_results[step_name] = result
                        print(f"✅ [{step_name}] Finalizat cu succes la încercarea {attempt}.")
                        success = True
                        break

                except Exception as e:
                    print(f"❌ [Exception] Eroare la rularea agentului: {e}")
                    last_error_context = str(e)

            if not success:
                error_msg = f"Pasul {step_name} a eșuat după {self.max_retries} încercări."
                state.errors.append(error_msg)
                print(f"💥 {error_msg}")
                break

        print("\n🏁 [Workflow Engine] Pipeline completat!" + "\n" + "="*70)
        return state