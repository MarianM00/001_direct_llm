# Multi-Agent AI Control Room

A local-first **multi-agent AI orchestration system** that transforms natural-language requests into executable workflows using specialized AI agents.

The system uses an LLM served through **LM Studio / Ollama** as its reasoning layer and coordinates multiple specialized agents through a sequential workflow engine. It includes **automatic error detection, self-correction, context propagation, persistent memory, tool execution, and a real-time Streamlit dashboard**.

The project was built to explore how autonomous AI systems can move beyond simple LLM chat and perform multi-step tasks through planning, execution, observation, and recovery.

---

## Overview

Instead of sending every request directly to an LLM, the system follows an agentic workflow:

```text
User Request
     │
     ▼
┌─────────────────┐
│  Planner Agent  │
│ Task Decompose  │
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│   Workflow Engine    │
│ Orchestration + State│
└──────────┬───────────┘
           │
     ┌─────┼─────────────┐
     ▼     ▼             ▼
┌────────┐ ┌────────┐ ┌────────────┐
│ System │ │ Coding │ │  Research  │
│ Agent  │ │ Agent  │ │   Agent    │
└────┬───┘ └────┬───┘ └─────┬──────┘
     │          │            │
     └──────────┼────────────┘
                ▼
       Context Manager
                │
                ▼
       Self-Correction
                │
                ▼
        Final Result
```

The system is designed around the principle that an LLM should act as a **reasoning and planning component**, while deterministic Python components handle execution, state management, file operations, and error handling.

---

## Key Features

### Multi-Agent Architecture

The system separates responsibilities across specialized agents instead of relying on a single general-purpose LLM.

Current agents include:

* **Planner Agent** — decomposes natural-language requests into structured JSON execution plans.
* **System Agent** — performs controlled operating-system interactions such as file inspection and environment information.
* **Coding Agent** — generates, validates, and executes Python code.
* **Research Agent** — manages persistent contextual information and memory.
* **Workflow Engine** — orchestrates agent execution and maintains workflow state.

This architecture makes individual capabilities easier to extend, test, and replace independently.

---

### LLM-Based Task Planning

The Planner Agent receives a natural-language request and generates a structured execution plan.

Example:

```text
"Analyze the Python files in this directory and create a report."
```

The planner can transform the request into a workflow such as:

```text
1. Inspect directory
2. Identify Python files
3. Analyze source code
4. Generate report
5. Store the resulting artifact
```

The planner uses structured output to separate **reasoning/planning from execution**.

---

### Context Propagation

The system includes a dedicated `ContextManager` responsible for passing relevant state between workflow steps.

Instead of executing agents independently, later agents receive information produced by previous agents.

Conceptually:

```text
Agent A
   │
   ├── result
   ├── observations
   └── execution state
          │
          ▼
    ContextManager
          │
          ▼
Agent B
```

This enables multi-step workflows where each agent can build upon previous execution results.

---

### Self-Correction & Error Recovery

One of the main features of the system is an automatic recovery mechanism for failed agent executions.

When an executable agent produces an error or traceback:

```text
Agent Execution
       │
       ▼
   Exception?
    /     \
  No       Yes
  │         │
  ▼         ▼
Continue   Capture
          traceback
             │
             ▼
       Update Context
             │
             ▼
        Retry Agent
             │
             ▼
      Corrected Result
```

The Workflow Engine captures execution failures, adds the relevant error information to the context, and allows the agent to retry with the additional information.

This creates a basic **observe → diagnose → correct → retry** loop rather than terminating the entire workflow after the first failure.

---

## Agents

### Planner Agent

**File:** `planner.py`

Responsibilities:

* Understand the user's natural-language request.
* Determine whether the request requires a multi-step workflow.
* Decompose complex tasks.
* Generate structured JSON execution plans.
* Select appropriate specialized agents.
* Provide a conversational fallback for requests that do not require workflow execution.

The planner currently uses a local LLM served through LM Studio.

---

### System Agent

**File:** `agents/system_agent.py`

Responsible for controlled system-level operations.

Examples include:

* File and directory inspection.
* Environment information.
* System state queries.
* Other deterministic OS-level operations exposed as tools.

The agent acts as an interface between the workflow and the local execution environment.

---

### Coding Agent

**File:** `agents/coding_agent.py`

Responsible for autonomous coding tasks.

Workflow:

```text
Generate Python
      ↓
Validate
      ↓
Execute
      ↓
Capture stdout/stderr
      ↓
Detect errors
      ↓
Retry with traceback
```

This agent demonstrates how an LLM can be combined with deterministic program execution rather than being used only for text generation.

---

### Research Agent

**File:** `agents/research_agent.py`

Responsible for persistent contextual information.

The current implementation stores information in:

```text
memory.md
```

This allows information produced during one workflow to be persisted and reused later.

---

## Workflow Engine

**File:** `workflow_engine.py`

The Workflow Engine is the central orchestration component.

Responsibilities include:

* Sequential agent execution.
* Workflow state management.
* Context propagation.
* Error detection.
* Self-correction and retry logic.
* Execution metrics.
* Agent status reporting.
* Communication with the Streamlit UI through callbacks.

The engine deliberately separates **orchestration logic from the UI layer**, allowing the workflow to be executed independently from the dashboard.

---

## Dashboard

**File:** `app.py`

The project includes a Streamlit dashboard for observing agent execution in real time.

### Agent Status

Displays the current state of each agent:

```text
● Active
○ Idle
```

The active agent is highlighted while the workflow is running.

### Pipeline Metrics

The dashboard displays:

* Pipeline status.
* Total execution time.
* Number of executed steps.
* Active LLM model.
* Agent execution state.

### Generated Artifacts

The dashboard automatically detects files created or modified during execution.

Supported artifacts include:

* `.py`
* `.txt`
* `.md`
* `.json`

Files can be inspected directly from the UI with syntax highlighting and downloaded individually.

---

## Architecture

```text
001_direct_llm/
│
├── app.py
│
├── planner.py
├── workflow_engine.py
├── context_manager.py
│
├── agents/
│   ├── __init__.py
│   ├── system_agent.py
│   ├── coding_agent.py
│   └── research_agent.py
│
├── memory.md
│
└── .venv/
```

### Design Principles

The architecture follows several principles:

* **Separation of concerns** — planning, orchestration, execution, memory, and UI are separated.
* **Specialized agents** — each agent has a focused responsibility.
* **Deterministic execution** — LLMs decide what should happen while application code controls how operations are executed.
* **Context-aware workflows** — execution state is passed between agents.
* **Fault tolerance** — execution failures can trigger automatic recovery.
* **Observable execution** — workflow state and metrics are exposed through the dashboard.
* **Extensibility** — new agents can be added without redesigning the entire workflow.

---

## LLM Infrastructure

The project is designed to run with locally hosted LLMs.

Current setup:

* **LM Studio**
* **Ollama-compatible local inference**
* **OpenAI-compatible API**
* `google/gemma-4-e4b` as the current planner model

Example endpoint:

```text
http://localhost:1234/v1
```

The application communicates with the local model using the OpenAI Python SDK.

This architecture allows the LLM provider to be replaced without changing the core agent orchestration logic.

---

## AI Development & Agentic Tooling

The project is also part of a broader exploration of **AI-assisted software engineering and autonomous coding agents**.

Tools and technologies explored alongside the project include:

* Local LLM inference with **LM Studio**
* **Ollama**
* OpenAI-compatible LLM APIs
* **Hermes Agent**
* GitHub Copilot
* Claude
* Cursor / AI coding workflows
* Prompt engineering
* Agent orchestration
* Tool calling
* Context management
* Autonomous code generation
* Self-correction loops

A particular focus is understanding how AI coding agents can be safely integrated into development workflows through isolated environments, controlled tool access, and deterministic execution.

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd 001_direct_llm
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the environment

macOS / Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install streamlit openai
```

### 5. Start the LLM server

Start LM Studio or Ollama and expose an OpenAI-compatible API.

For LM Studio, the default local endpoint is:

```text
http://localhost:1234/v1
```

Make sure the configured model is available.

### 6. Test the Planner

```bash
python -c "from planner import create_plan; print(create_plan('arată-mi fișierele'))"
```

### 7. Start the Dashboard

```bash
streamlit run app.py
```

The dashboard will be available at:

```text
http://localhost:8501
```

---

## Example Workflow

A request such as:

```text
"Create a Python script that analyzes the files in this directory and save the results to report.md"
```

can result in:

```text
User Request
     ↓
Planner Agent
     ↓
Execution Plan
     ↓
System Agent
     ↓
Directory Inspection
     ↓
Coding Agent
     ↓
Generate Python
     ↓
Execute Script
     ↓
Error?
 ┌───┴───┐
 No     Yes
 │       │
 ▼       ▼
Continue Traceback
           ↓
      Self-Correction
           ↓
          Retry
           ↓
      Research Agent
           ↓
      Persist Result
           ↓
       Final Output
```

---

## Technology Stack

| Area               | Technology                                   |
| ------------------ | -------------------------------------------- |
| Language           | Python                                       |
| LLM                | Local LLMs                                   |
| Inference          | LM Studio / Ollama                           |
| LLM API            | OpenAI-compatible API                        |
| Agent Architecture | Multi-Agent System                           |
| Orchestration      | Custom Workflow Engine                       |
| Context            | Custom Context Manager                       |
| Memory             | Markdown-based persistence                   |
| UI                 | Streamlit                                    |
| AI Tooling         | Hermes Agent, GitHub Copilot, Claude, Cursor |
| Execution          | Python subprocess / local tools              |

---

## What I Explored

This project focuses on the engineering challenges behind autonomous AI systems rather than simply integrating an LLM API.

Key areas explored:

* Designing multi-agent architectures.
* Decomposing complex tasks into executable workflows.
* Passing state and context between agents.
* Combining probabilistic LLM reasoning with deterministic application logic.
* Executing AI-generated code safely.
* Detecting runtime failures and automatically recovering.
* Maintaining persistent agent memory.
* Building observable agent workflows.
* Running LLMs locally instead of relying exclusively on cloud APIs.
* Integrating AI coding agents into software development workflows.

The project serves as a foundation for experimenting with more advanced capabilities such as tool calling, parallel agent execution, sandboxed execution, long-term memory, and human-in-the-loop workflows.
