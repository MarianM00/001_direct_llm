# test_workflow.py
from workflow_engine import SequentialWorkflowEngine

def main():
    engine = SequentialWorkflowEngine()

    # Definim lanțul secvențial de pași
    pipeline_steps = [
        {
            "agent": "system", 
            "task": "Verifică lista fișierelor din directorul curent și ora actuală."
        },
        {
            "agent": "coding", 
            "task": "Creează un script Python numit 'audit_report.py' care scrie într-un fișier text 'report.txt' ora curentă și fișierele găsite la pasul anterior, apoi execută-l."
        },
        {
            "agent": "research", 
            "task": "Salvează în memorie faptul că am creat un raport de audit numit 'report.txt' în director."
        }
    ]

    # Rulăm pipeline-ul
    final_state = engine.run_pipeline(
        steps=pipeline_steps, 
        user_goal="Audit al directorului curent și generare raport"
    )

    # Afișăm rezultatul final agregat
    print("\n📊 REZULTAT FINAL WORKFLOW:")
    for step, output in final_state.step_results.items():
        print(f"\n--- {step} ---")
        print(output)

if __name__ == "__main__":
    main()