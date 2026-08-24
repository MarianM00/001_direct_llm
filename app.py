# app.py
import os
import time
import streamlit as st

from planner import create_plan
from workflow_engine import SequentialWorkflowEngine

# Configurare Pagină
st.set_page_config(
    page_title="Multi-Agent Control Room",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS pentru Carduri Elegante
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
        """Această funcție va fi apelată din Workflow Engine la fiecare pas."""
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

    # 3. REZULTAT FINAL FORMATAT
    st.divider()
    st.subheader("✨ Rezultat Final (Formatted Output)")
    
    m1, m2 = st.columns(2)
    m1.metric("Timp Execuție Total", f"{exec_time}s")
    m2.metric("Pași Executați", f"{len(steps)}")

    for step_key, result_text in final_state.step_results.items():
        clean_text = str(result_text).replace("\\n", "\n")
        
        with st.container():
            st.markdown(f"### 📌 Output `{step_key}`")
            st.markdown(f'<div class="output-box">{clean_text}</div>', unsafe_allow_html=True)
            st.write("")