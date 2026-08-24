import json
from openai import OpenAI
from guardrails import request_approval

class BaseAgent:
    def __init__(self, name: str, model: str, system_prompt: str, tools: list, max_steps: int = 6):
        self.name = name
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools
        self.max_steps = max_steps
        self.client = OpenAI(
            base_url="http://100.97.106.90:1234/v1",
            api_key="lm-studio",
        )
        self.tool_map = {}

    def register_tool(self, name: str, func):
        """Asociază numele tool-ului din JSON cu funcția sa Python."""
        self.tool_map[name] = func

    def run(self, user_message: str, history: list = None) -> str:
        print(f"\n🤖 [{self.name}] Preluat sarcina cu modelul: {self.model}")
        
        messages = [{"role": "system", "content": self.system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        step = 1
        while step <= self.max_steps:
            print(f"--- [{self.name} - Pasul {step}/{self.max_steps}] ---")
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 800,
            }
            if self.tools:
                kwargs["tools"] = self.tools
                kwargs["tool_choice"] = "auto"

            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message
            messages.append(message)

            if message.tool_calls:
                if message.content:
                    print(f"🧠 [Thought]: {message.content}")

                for tool_call in message.tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments or "{}")

                    print(f"⚙️ [Action Propusă]: Apel '{name}' cu argumente: {args}")

                    # --- Human Approval Guardrail Check ---
                    if not request_approval(name, args):
                        result = "Eroare: Acțiunea a fost RESPINSĂ de către utilizator."
                    else:
                        if name in self.tool_map:
                            func = self.tool_map[name]
                            # Extrage parametrii și apelează funcția
                            result = func(**args) if args else func()
                        else:
                            result = f"Eroare: Tool-ul '{name}' nu este înregistrat."

                    print(f"👁️ [Observation]: {result}\n")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),
                    })
                step += 1
            else:
                final_answer = message.content or "Sarcina a fost finalizată."
                print(f"🏁 [{self.name} Răspuns Final]:\n")
                return final_answer

        return "❌ S-a atins limita maximă de pași fără finalizare."