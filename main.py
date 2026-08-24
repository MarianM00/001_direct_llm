# main.py
import sys
from planner import create_plan
from workflow_engine import SequentialWorkflowEngine

def main():
    if len(sys.argv) < 2:
        print("⚠️ Utilizare: python main.py \"Cererea ta complexă aici...\"")
        sys.exit(1)

    user_query = sys.argv[1]
    print(f"\n📥 Cerere Utilizator: '{user_query}'")

    # 1. Planner-ul analizează cererea și generează pașii
    print("\n🧠 [Planner] Analizez cererea și generez planul de execuție...")
    steps = create_plan(user_query)

    if not steps:
        print("❌ Nu s-a putut genera un plan valid. Verifică conexiunea la model sau promptul.")
        return

    # 2. Afișăm planul generat de LLM
    print(f"\n📋 Plan Automat Generat ({len(steps)} pași):")
    for idx, step in enumerate(steps, 1):
        print(f"  {idx}. [{step['agent'].upper()}] -> {step['task']}")

    # 3. Executăm planul prin Workflow Engine
    engine = SequentialWorkflowEngine()
    final_state = engine.run_pipeline(steps=steps, user_goal=user_query)

    if final_state.errors:
        print("\n⚠️ Workflow-ul s-a încheiat cu avertismente/erori:")
        for err in final_state.errors:
            print(f"  - {err}")
    else:
        print("\n✨ TOȚI PAȘII AU FOST EXECUTAȚI CU SUCCES DE CĂTRE AGENȚI!")

if __name__ == "__main__":
    main()