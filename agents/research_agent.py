from agents.base_agent import BaseAgent
from tools.memory_tools import read_memory, write_memory

class ResearchAgent(BaseAgent):
    def __init__(self):
        system_prompt = """Ești un Cercetător și Asistent de Cunoștințe.
Rolul tău este să oferi explicații clare, să cauți în memorie sau să salvezi informații importante pe termen lung.
Formatează răspunsurile scurt, structurat și ușor de citit."""

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_memory",
                    "description": "Caută sau citește informații din memoria pe termen lung",
                    "parameters": {
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_memory",
                    "description": "Salvează notițe sau fapte în memorie",
                    "parameters": {
                        "type": "object",
                        "properties": {"content": {"type": "string"}},
                        "required": ["content"]
                    }
                }
            }
        ]

        super().__init__(
            name="Research Agent",
            model="google/gemma-4-e4b",
            system_prompt=system_prompt,
            tools=tools,
            max_steps=5
        )

        self.register_tool("read_memory", read_memory)
        self.register_tool("write_memory", write_memory)