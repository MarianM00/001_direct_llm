from datetime import datetime
from agents.base_agent import BaseAgent
from tools.file_tools import list_files, read_file

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class SystemAgent(BaseAgent):
    def __init__(self):
        system_prompt = """Ești un Administrator de Sistem. Rolul tău este să inspectezi structura directoarelor, să listezi fișiere și să oferi informații despre stare și timp."""

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "Listează fișierele din director",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string"}},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Citește conținutul unui fișier",
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
                    "name": "get_current_time",
                    "description": "Returnează ora și data curentă",
                    "parameters": {"type": "object", "properties": {}, "required": []}
                }
            }
        ]

        super().__init__(
            name="System Agent",
            model="google/gemma-4-e4b",
            system_prompt=system_prompt,
            tools=tools,
            max_steps=4
        )

        self.register_tool("list_files", list_files)
        self.register_tool("read_file", read_file)
        self.register_tool("get_current_time", get_current_time)