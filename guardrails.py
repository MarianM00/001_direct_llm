SENSITIVE_TOOLS = ["write_file", "execute_python"]

def request_approval(tool_name: str, args: dict) -> bool:
    """Solicită aprobarea utilizatorului în consolă pentru acțiuni critice."""
    if tool_name not in SENSITIVE_TOOLS:
        return True

    print("\n" + "="*50)
    print(f"⚠️  [HUMAN APPROVAL REQUIRED]")
    print(f"Action: '{tool_name}'")
    print(f"Arguments: {args}")
    print("="*50)
    
    response = input("Aprobi executarea acestei acțiuni? (y/N): ").strip().lower()
    if response in ["y", "yes", "da"]:
        print("✅ Acțiune aprobată de utilizator.\n")
        return True
    else:
        print("❌ Acțiune respinsă de utilizator.\n")
        return False