import os
import subprocess
import sys

def list_files(path="."):
    """Listează fișierele din directorul specificat."""
    try:
        return "\n".join(os.listdir(path))
    except Exception as e:
        return f"Eroare: {e}"

def read_file(path):
    """Citește conținutul unui fișier."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Eroare: {e}"

def write_file(path, content):
    """Scrie sau suprascrie un fișier cu noul conținut."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Fișierul '{path}' a fost scris cu succes."
    except Exception as e:
        return f"Eroare la scriere: {e}"

def execute_python(path: str):
    """Execută un fișier Python local și returnează output-ul sau eroarea."""
    if not os.path.exists(path):
        return f"Eroare: Fișierul '{path}' nu există."
    try:
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            out = result.stdout if result.stdout else "(fără output)"
            return f"✅ Execuție cu succes!\nOutput:\n{out}"
        else:
            return f"❌ Eroare la execuție (Code {result.returncode}):\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "❌ Eroare: Scriptul a depășit timpul maxim de execuție (Timeout 10s)."
    except Exception as e:
        return f"❌ Eroare neașteptată la execuție: {e}"