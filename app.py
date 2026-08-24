# app.py
import os
import streamlit as st

from planner import create_plan
from workflow_engine import SequentialWorkflowEngine

# Setări pagină
st.set_page_config(
    page_title="Multi-Agent AI Control Center",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Multi-Agent AI System Dashboard")
st.caption("Arhitectură autonomă cu Planner, System, Coding & Research Agents + Self-Correction")

# Sidebar
with st.sidebar:
    st.header("⚙️ Setări Pipeline")
    max_retries = st.number_input("Max Retries (Self-Correction)", min_value=1, max_value=5, value=3)
    auto_approve = st.checkbox("Auto-Approve Actions", value=True)
    
    st.divider()
    st.header("📁 Workspace Inspector")
    files = [f for f in os.listdir(".") if not f.startswith(".")]
    selected_file = st.selectbox("Alege un fișier:", sorted(files))
    
    if selected_file and os.path.isfile(selected_file):
        with st.expander(f"📄 {selected_file}"):
            try:
                with open(selected_file, "r", encoding="utf-8") as f:
                    st.code(f.read(), language="python" if selected_file.endswith(".py") else "text")
            except Exception as e:
                st.error(f"Eroare citire: {e}")

# Zona Principală
user_prompt = st.text_area(
    "💬 Introduceți sarcina pentru agenți:",
    value="Vezi ce fișiere am în director, creează un script numit gen_ora.py care scrie ora și fișierele găsite într-un fișier ora.txt și execută-l, iar la final salvează în memorie că am creat ora.txt.",
    height=100
)

col1, _ = st.columns([1, 4])
with col1:
    start_btn = st.button("🚀 Lansare Pipeline", type="primary", use_container_width=True)

if start_btn and user_prompt:
    st.divider()
    
    # 1. Generare Plan
    with st.status("🧠 [Planner] Analizez cererea și generez planul...", expanded=True) as status:
        try:
            steps = create_plan(user_prompt)
        except Exception as err:
            steps = []
            st.error(f"❌ Eroare la apelarea Planner-ului: {err}")

        if not steps:
            st.error("⚠️ Planner-ul a returnat un plan gol! Verifică log-ul din terminal pentru `❌ [Planner Error]` (Ex: Nume model incorect sau server oprit).")
            status.update(label="❌ Generare plan eșuată", state="error", expanded=True)
            st.stop()
        
        st.subheader("📋 Plan de Execuție Generat:")
        for idx, step in enumerate(steps, 1):
            st.markdown(f"**Pasul {idx}** `[{step['agent'].upper()}]`: {step['task']}")
        
        status.update(label="✅ Plan generat cu succes!", state="complete", expanded=False)

    # 2. Console Logs
    st.subheader("⚙️ Live Agent Execution Console")
    log_container = st.empty()
    logs_list = []

    def stream_logger(msg: str):
        logs_list.append(msg)
        log_container.code("\n".join(logs_list), language="text")

    # 3. Engine Run
    engine = SequentialWorkflowEngine(max_retries=max_retries, auto_approve=auto_approve)
    
    with st.spinner("🤖 Agenții lucrează..."):
        final_state = engine.run_pipeline(steps, user_prompt, log_callback=stream_logger)

    # 4. Results
    st.divider()
    if final_state.errors:
        st.error(f"❌ Pipeline-ul s-a încheiat cu erori: {final_state.errors}")
    else:
        st.success("🎉 Toți pașii au fost executați cu succes!")
        with st.expander("📊 Rezultate detaliate"):
            st.json(final_state.step_results)