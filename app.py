import os
import time
import streamlit as st

from planner import create_plan
from workflow_engine import SequentialWorkflowEngine

# Configurare Pagină
st.set_page_config(
    page_title="Agent System Dashboard",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS pentru a-l apropia de design-ul din imagine (Dark Minimalist Cards)
st.markdown("""
<style>
    .agent-card {
        background-color: #1e222d;
        border: 1px solid #2e3440;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
    }
    .status-active {
        color: #4CAF50;
        font-weight: bold;
    }
    .status-idle {
        color: #888888;
    }
    .output-box {
        background-color: #14161d;
        border-radius: 8px;
        padding: 20px;
        border-left: 4px solid #4F46E5;
        font-size: 15px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Multi-Agent Control Center")

# --- TOP PANEL: AGENT STATUS CARDS ---
st.subheader("🤖 Your Agent Team")

# Inițializăm starea agenților
active_agent = st.session_state.get("active_agent", "None")

col_router, col_system, col_coding, col_research = st.columns(4)

with col_router:
    is_act = active_agent == "planner"
    st.markdown(f"""
    <div class="agent-card">
        <h3>🧠 Planner</h3>
        <p class="{ 'status-active' if is_act else 'status-idle' }">{ '● Active' if is_act else '○ Idle' }</p>
        <small>Routing & Task Decomposition</small>
    </div>
    """, unsafe_allow_html=True)

with col_system:
    is_act = active_agent == "system"
    st.markdown(f"""
    <div class="agent-card">
        <h3>⚙️ System</h3>
        <p class="{ 'status-active' if is_act else 'status-idle' }">{ '● Active' if is_act else '○ Idle' }</p>
        <small>OS Operations & Environment</small>
    </div>
    """, unsafe_allow_html=True)

with col_coding:
    is_act = active_agent == "coding"
    st.markdown(f"""
    <div class="agent-card">
        <h3>💻 Coding</h3>
        <p class="{ 'status-active' if is_act else 'status-idle' }">{ '● Active' if is_act else '○ Idle' }</p>
        <small>Python Execution & Logic</small>
    </div>
    """, unsafe_allow_html=True)

with col_research:
    is_act = active_agent == "research"
    st.markdown(f"""
    <div class="agent-card">
        <h3>📚 Research</h3>
        <p class="{ 'status-active' if is_act else 'status-idle' }">{ '● Active' if is_act else '○ Idle' }</p>
        <small>Memory & Context Storage</small>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- INPUT SECTION ---
user_prompt = st.text_input(
    "💬 Introduceți sarcina sau mesajul pentru agenți:",
    value="Arată-mi ce fișiere am în director și spune-mi ora curentă."
)

if st.button("🚀 Lansare Pipeline", type="primary"):
    start_time = time.time()
    
    # Setăm status planner
    st.session_state["active_agent"] = "planner"
    
    # 1. PLANNER
    with st.spinner("Planner-ul analizează..."):
        steps = create_plan(user_prompt)

    if not steps:
        st.warning("💬 Niciun pas de execuție generat (Conversație simplă sau răspuns direct).")
        st.session_state["active_agent"] = "None"
        st.stop()

    st.subheader("📋 Plan de Execuție")
    for idx, step in enumerate(steps, 1):
        st.caption(f"Pasul {idx} **[{step['agent'].upper()}]**: {step['task']}")

    # 2. EXECUTION ENGINE
    st.divider()
    st.subheader("⚙️ Live Execution Console")
    
    log_container = st.empty()
    logs_list = []

    def stream_logger(msg: str):
        logs_list.append(msg)
        log_container.code("\n".join(logs_list), language="text")

    engine = SequentialWorkflowEngine(max_retries=3, auto_approve=True)
    
    # Rulăm pipeline-ul
    final_state = engine.run_pipeline(steps, user_prompt, log_callback=stream_logger)
    
    st.session_state["active_agent"] = "None"
    exec_time = round(time.time() - start_time, 2)

    # 3. AFISARE REZULTATE ELEGANTE (Curățate de \n)
    st.divider()
    st.subheader("✨ Rezultat Final (Formatted Output)")
    
    # Metrică de performanță
    col1, col2 = st.columns(2)
    col1.metric("Timp Execuție", f"{exec_time}s")
    col2.metric("Pași Executați", f"{len(steps)}")

    # Afișăm rezultatele frumos, decodificând character-ele de escape (\n)
    for step_key, result_text in final_state.step_results.items():
        # Înlocuim caracterul textual '\n' cu enter real
        clean_text = str(result_text).replace("\\n", "\n")
        
        with st.container():
            st.markdown(f"### 📌 Output {step_key}")
            st.markdown(f'<div class="output-box">{clean_text}</div>', unsafe_allow_html=True)