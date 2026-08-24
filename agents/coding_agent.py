from agents.base_agent import BaseAgent
from tools.file_tools import write_file, read_file, execute_python

class CodingAgent(BaseAgent):
    def __init__(self):
        system_prompt = """Ești un Agent de Programare Python (Senior Engineer).

REGULĂ STRICTĂ ȘI ABSOLUTĂ:
- NU poți finaliza sarcina (NU da 'Răspuns Final') fără să apelezi MAI ÎNTÂI un Tool!
- Dacă sarcina cere să creezi un fișier -> Apelează OBLIGATORIU tool-ul 'write_file'.
- Dacă sarcina cere să rulezi un fișier -> Apelează OBLIGATORIU tool-ul 'execute_python'.
- Dacă dintr-un motiv oarecare nu poți apela tool-ul, generează codul și apelează 'write_file' oricum!

Formatul de apel al tool-urilor trebuie să fie strict cel pe care îl cunoști. NU răspunde doar cu text!"""

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