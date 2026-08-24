# workflow_engine.py
from dataclasses import dataclass, field
from typing import Dict, Any, List
import os

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
    
    def __init__(self, max_retries: int = 3, auto_approve: bool = False):
        self.max_retries = max_retries
        self.auto_approve = auto_approve
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
        critical_errors = [
            "Traceback (most recent call last):",
            "❌ Eroare la execuție",
            "SyntaxError:",
            "IndentationError:"
        ]
        return any(keyword in res_str for keyword in critical_errors)

    def run_pipeline(self, steps: List[Dict[str, str]], user_goal: str, log_callback=None) -> WorkflowState:
        state = WorkflowState(user_goal=user_goal)
        
        def log(msg: str):
            print(msg)
            if log_callback:
                log_callback(msg)

        log(f"🚀 [Workflow Engine] Start Pipeline cu Self-Correction pentru: '{user_goal}'")

        for i, step in enumerate(steps, 1):
            agent_type = step["agent"]
            specific_task = step["task"]
            step_name = f"Pasul_{i}_{agent_type}"

            log(f"\n🔄 [Workflow Step {i}/{len(steps)}] -> Agent: [{agent_type.upper()}]")
            log(f"🎯 Sarcina: {specific_task}")

            if agent_type not in self.agent_registry:
                error_msg = f"Agentul '{agent_type}' nu este înregistrat!"
                state.errors.append(error_msg)
                log(f"❌ {error_msg}")
                break

            agent = self.agent_registry[agent_type]
            success = False
            last_error_context = ""

            for attempt in range(1, self.max_retries + 1):
                if attempt > 1:
                    log(f"\n🔄 [SELF-CORRECTION] Încercarea {attempt}/{self.max_retries} pentru {step_name}...")

                formatted_context = ContextManager.format_context_for_agent(state.step_results)
                
                if last_error_context:
                    formatted_context += f"\n⚠️ [EROARE LA ÎNCERCAREA ANTERIOARĂ]:\n{last_error_context}\n"
                    task_with_correction = f"{specific_task} (Corectează eroarea apărută anterior!)"
                else:
                    task_with_correction = specific_task

                combined_prompt = ContextManager.build_actionable_prompt(task_with_correction, formatted_context)

                try:
                    result = self._execute_agent(agent, combined_prompt)

                    if self._is_error_output(result):
                        log(f"⚠️ [Workflow Engine] S-a detectat o eroare în output la încercarea {attempt}!")
                        last_error_context = str(result)
                    else:
                        state.step_results[step_name] = result
                        log(f"✅ [{step_name}] Finalizat cu succes la încercarea {attempt}.")
                        success = True
                        break

                except Exception as e:
                    log(f"❌ [Exception] Eroare la rularea agentului: {e}")
                    last_error_context = str(e)

            if not success:
                error_msg = f"Pasul {step_name} a eșuat după {self.max_retries} încercări."
                state.errors.append(error_msg)
                log(f"💥 {error_msg}")
                break

        log("\n🏁 [Workflow Engine] Pipeline completat!")
        return state