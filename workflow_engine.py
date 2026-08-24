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
    """Orchestrator care rulează agenții secvențial cu Context Management avansat."""
    
    def __init__(self):
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

    def run_pipeline(self, steps: List[Dict[str, str]], user_goal: str) -> WorkflowState:
        state = WorkflowState(user_goal=user_goal)
        print(f"\n🚀 [Workflow Engine] Start Pipeline pentru obiectivul: '{user_goal}'\n" + "="*70)

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

            # 1. GENERĂM CONTEXTUL STRUCTURAT (Context Management)
            formatted_context = ContextManager.format_context_for_agent(state.step_results)

            # 2. CONSTRUIM PROMPT-UL ACTIONABIL (Evită halucinațiile)
            combined_prompt = ContextManager.build_actionable_prompt(specific_task, formatted_context)

            try:
                agent = self.agent_registry[agent_type]
                result = self._execute_agent(agent, combined_prompt)

                state.step_results[step_name] = result
                print(f"✅ [{step_name}] Finalizat cu succes.")

            except Exception as e:
                error_msg = f"Eroare la executarea pasului {step_name}: {str(e)}"
                state.errors.append(error_msg)
                print(f"❌ {error_msg}")
                break

        print("\n🏁 [Workflow Engine] Pipeline completat!" + "\n" + "="*70)
        return state