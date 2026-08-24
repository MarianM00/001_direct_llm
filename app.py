import os
import time
import glob
import streamlit as st

from planner import create_plan, PLANNER_MODEL
from workflow_engine import SequentialWorkflowEngine

# Configurare Pagină
st.set_page_config(
    page_title="Multi-Agent Control Room",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS pentru Carduri & Interfață Pro
st.markdown("""
<style>
    .agent-card {
        background-color: #1e222d;
        border: 1px solid #2e3440;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .agent-card-active {
        background-color: #1a2e22;
        border: 2px solid #22c55e;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 0 15px rgba(34, 197, 94, 0.2);
    }
    .status-active {
        color: #22c55e;
        font-weight: bold;
        font-size: 1.1em;
    }
    .status-idle {
        color: #6b7280;
        font-size: 1.0em;
    }
    .output-box {
        background-color: #14161d;
        border-radius: 8px;
        padding: 20px;
        border-left: 4px solid #6366f1;
        font-size: 15px;
        line-height: 1.6;
    }
    .artifact-card {
        background-color: #181b24;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Multi-Agent Control Room")

# Container dinamic pentru Cardurile de Status
status_container = st.empty()

def render_agent_cards(active_agent_name: str = "idle"):
    """Randează cardurile cu agentul activ marcat în verde."""
    active_agent_name = active_agent_name.lower()
    
    with status_container.container():
        st.subheader("🤖 Your Agent Team")
        c1, c2, c3, c4 = st.columns(4)
        
        agents = [
            ("planner", "🧠 Planner", "Routing & Task Decomposition"),
            ("system", "⚙️ System", "OS Operations & Environment"),
            ("coding", "💻 Coding", "Python Execution & Logic"),
            ("research", "📚 Research", "Memory & Context Storage")
        ]
        
        cols = [c1, c2, c3, c4]
        for col, (a_id, title, desc) in zip(cols, agents):
            is_active = (active_agent_name == a_id)
            card_class = "agent-card-active" if is_active else "agent-card"
            status_html = '<span class="status-active">● Active</span>' if is_active else '<span class="status-idle">○ Idle</span>'
            
            col.markdown(f"""
            <div class="{card_class}">
                <h3 style="margin-bottom:5px;">{title}</h3>
                <p>{status_html}</p>
                <small style="color:#9ca3af;">{desc}</small>
            </div>
            """, unsafe_allow_html=True)

def get_workspace_files():
    """Returnează un dicționar cu fișierele din workspace și timestamp-ul ultimei modificări."""
    files = {}
    extensions = ['*.txt', '*.py', '*.json', '*.csv', '*.md', '*.log']
    for ext in extensions:
        for filepath in glob.glob(ext):
            files[filepath] = os.path.getmtime(filepath)
    return files

# Afișăm inițial toate cardurile pe "Idle"
render_agent_cards("idle")

st.divider()

# --- INPUT SECTION ---
user_prompt = st.text_input(
    "💬 Introduceți sarcina sau mesajul pentru agenți:",
    value="Arată-mi ce fișiere am în director și spune-mi ora curentă."
)

if st.button("🚀 Lansare Pipeline", type="primary"):
    start_time = time.time()
    initial_files = get_workspace_files()
    
    # 1. PLANNER ACTIVE
    render_agent_cards("planner")
    
    with st.spinner("Planner-ul analizează cererea..."):
        steps = create_plan(user_prompt)

    if not steps:
        st.warning("💬 Niciun pas de execuție generat.")
        render_agent_cards("idle")
        st.stop()

    st.subheader("📋 Plan de Execuție Generat")
    for idx, step in enumerate(steps, 1):
        st.caption(f"Pasul {idx} **[{step['agent'].upper()}]**: {step['task']}")

    # 2. CONSOLE LOGS & LIVE EXECUTION
    st.divider()
    st.subheader("⚙️ Live Execution Console")
    
    log_container = st.empty()
    logs_list = []

    def stream_logger(msg: str):
        logs_list.append(msg)
        log_container.code("\n".join(logs_list), language="text")

    def live_status_update(agent_type: str):
        render_agent_cards(agent_type)

    engine = SequentialWorkflowEngine(max_retries=3, auto_approve=True)
    
    # Executăm pipeline-ul
    final_state = engine.run_pipeline(
        steps=steps, 
        user_goal=user_prompt, 
        log_callback=stream_logger,
        status_callback=live_status_update
    )
    
    # Resetăm agenții la Idle după finalizare
    render_agent_cards("idle")
    exec_time = round(time.time() - start_time, 2)
    has_errors = len(getattr(final_state, 'errors', [])) > 0
    pipeline_status = "❌ Failed" if has_errors else "✅ Completed"

    # 3. METRICS BAR COMPLETĂ
    st.divider()
    st.subheader("📊 System Metrics & Performance")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Status Pipeline", pipeline_status)
    m2.metric("Timp Execuție Total", f"{exec_time}s")
    m3.metric("Pași Executați", f"{len(steps)}")
    m4.metric("Model Utilizat", PLANNER_MODEL.split("/")[-1] if "/" in PLANNER_MODEL else PLANNER_MODEL)

    # 4. REZULTAT FINAL FORMATAT
    st.divider()
    st.subheader("✨ Rezultat Final (Formatted Output)")
    
    for step_key, result_text in final_state.step_results.items():
        clean_text = str(result_text).replace("\\n", "\n")
        
        with st.container():
            st.markdown(f"### 📌 Output `{step_key}`")
            st.markdown(f'<div class="output-box">{clean_text}</div>', unsafe_allow_html=True)
            st.write("")

    # 5. FORMATTED ARTIFACTS VIEWER
    current_files = get_workspace_files()
    # Identificăm fișierele noi sau modificate în timpul acestei rulări
    created_or_modified = [
        f for f, mtime in current_files.items()
        if f not in initial_files or mtime > start_time
    ]

    if created_or_modified:
        st.divider()
        st.subheader("📁 Generated Artifacts & Files")
        st.info(f"S-au detectat **{len(created_or_modified)}** fișiere create sau modificate în timpul execuției.")
        
        for file_path in created_or_modified:
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].replace(".", "")
            
            # Determinăm limbajul pentru Syntax Highlighting
            lang_map = {"py": "python", "json": "json", "md": "markdown", "csv": "csv", "txt": "text"}
            syntax_lang = lang_map.get(file_ext, "text")

            with st.expander(f"📄 Fișier: `{file_name}`", expanded=True):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()

                    st.code(file_content, language=syntax_lang)
                    
                    st.download_button(
                        label=f"⬇️ Descarcă {file_name}",
                        data=file_content,
                        file_name=file_name,
                        mime="text/plain",
                        key=f"dl_{file_name}"
                    )
                except Exception as e:
                    st.error(f"Nu s-a putut citi fișierul {file_name}: {e}")