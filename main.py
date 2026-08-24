import sys
from router import route_intent
from agents.coding_agent import CodingAgent
from agents.research_agent import ResearchAgent
from agents.system_agent import SystemAgent
from tools.memory_tools import load_history, save_history

# Inițializare agenți
AGENTS = {
    "coding": CodingAgent(),
    "research": ResearchAgent(),
    "system": SystemAgent(),
}

def main():
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        # Prompt de test implicit
        user_query = "Creează un fișier numit prime.py care să verifice dacă 29 este număr prim și să-l ruleze."

    print("=" * 60)
    print(f"📥 Query Utilizator: '{user_query}'")
    print("=" * 60)

    # 1. Routing
    agent_key = route_intent(user_query)
    selected_agent = AGENTS.get(agent_key, AGENTS["research"])
    
    print(f"🔀 Intentie detectată -> A fost selectat: [{selected_agent.name}]")

    # 2. Încarcă istoricul de conversație
    history = load_history(limit=4)

    # 3. Execuție agent
    result = selected_agent.run(user_query, history=history)

    # 4. Salvare în istoric
    save_history(user_query, result)

    print("\n" + "=" * 60)
    print("✨ RĂSPUNS FINAL:")
    print(result)
    print("=" * 60)

if __name__ == "__main__":
    main()