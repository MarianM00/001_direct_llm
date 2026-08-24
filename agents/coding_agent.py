from agents.base_agent import BaseAgent
from tools.file_tools import write_file, read_file, execute_python

class CodingAgent(BaseAgent):
    def __init__(self):
        system_prompt = """Ești un Inginer Software Senior specializat în Python.
Regulile tale de lucru:
1. Scrie cod curat, modular și eficient.
2. Salvează codul în fișiere folosind 'write_file'.
3. Execută ÎNTOTDEAUNA fișierele create/modificate folosind 'execute_python' pentru a valida că nu există erori.
4. Dacă apar erori la execuție, analizează stack trace-ul, rescrie codul corectat și execută-l din nou (Self-Correction Loop).
5. Nu oferi răspunsul final până nu ai confirmat că totul rulează perfect."""

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Scrie conținut în fișier",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Citește un fișier de pe disc",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string"}},
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_python",
                    "description": "Execută un script Python și returnează output-ul sau eroarea",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string"}},
                        "required": ["path"]
                    }
                }
            }
        ]

        super().__init__(
            name="Coding Agent",
            model="qwen/qwen3.5-9b",
            system_prompt=system_prompt,
            tools=tools,
            max_steps=8
        )
        
        # Înregistrare funcții
        self.register_tool("write_file", write_file)
        self.register_tool("read_file", read_file)
        self.register_tool("execute_python", execute_python)