 #  AgentWeb+ — Multi-Agent AI System for Technical Interview Preparation

> Five specialized AI agents collaborate through a shared MCP-style context to plan, research, code, give feedback, and simulate interviews — all inside one interactive Streamlit web app.

---

##  Live Demo
🔗 **Try it here:** https://agentweb-multi-agent-ai-system-for.onrender.com

---

##  Overview
**AgentWeb+** is a modular **multi-agent system** built with Python and Streamlit that helps candidates prepare for **technical interviews in Computer Science, Data Science, and Machine Learning**.  
Each agent has a focused role — Planner, Researcher, Coder, Feedback Reviewer, and Mock Interviewer — and they coordinate using a shared context (similar to Model Context Protocol, MCP).

The result is an **AI-orchestrated interview coach** that can:
- Plan your study roadmap.
- Research learning resources.
- Solve and explain coding problems.
- Review your code and answers.
- Conduct adaptive mock interviews.

---

##  Multi-Agent Architecture

| Agent | Responsibility |
|:--|:--|
|  **Planner Agent** | Breaks your goal (e.g., “ML internship at Amazon in 4 weeks”) into a 4-week plan. |
|  **Research Agent** | Fetches summaries, definitions, and curated references. |
|  **Coding Agent** | Solves DS/Algo problems with explanations. |
|  **Feedback Agent** | Reviews your code or answers and gives structured feedback. |
|  **Mock Interview Agent** | Conducts mock interviews, scores responses, and stores results. |

All agents share a central **ContextStore** that tracks your progress and memory across sessions.

---

##  System Architecture

```text
┌────────────────────────────────────────┐
│              Streamlit UI              │
│ (Planner | Research | Coding | ... )   │
└────────────────────────────────────────┘
                  │
                  ▼
        ┌───────────────────┐
        │   MCP Core Layer  │
        │ (context_store.py │
        │  + model_router)  │
        └───────────────────┘
                  │
                  ▼
        ┌───────────────────┐
        │  OpenAI API (LLMs)│
        │  PostgreSQL (DB)  │
        └───────────────────┘

```
## Tech Stack

**Core Frameworks**

- Python 3.11

- Streamlit 1.37 (frontend + backend integration)

- FastAPI-style internal logic for agents (via MCP interface)

- PostgreSQL (session and mock-interview persistence)

- Docker + Render (containerized deployment)

**AI / LLM Integration**

- OpenAI API (gpt-3.5-turbo / gpt-4o-mini)

---
## Local Development

```bash
#  Clone the repo
git clone (https://github.com/AditiJha26/AgentWeb-Multi-Agent-AI-System-for-Technical-Interview-Preparation-and-Practice.git)
cd agentwebplus

#  Create virtual environment
python -m venv venv
venv\Scripts\activate  # (Windows)
# or source venv/bin/activate (Mac/Linux)

#  Install dependencies
pip install -r requirements.txt

#  Create a .env file
echo OPENAI_API_KEY=sk-... > .env
echo DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/agentwebplus?sslmode=require >> .env

#  Run locally
$env:PYTHONPATH="$PWD"
streamlit run app/streamlit_ui.py

# Build and run
docker compose up --build
# Then open your browser at:
# http://localhost:8501

---
## Deployment (Render)

Backend & UI: Deployed from Dockerfile on Render Web Service
Database: Managed PostgreSQL on Render

**Environment Variables:**

OPENAI_API_KEY = your API key
DATABASE_URL   = Render connection string (postgresql+psycopg://...)

Render automatically builds and redeploys the latest version of your app on every git push.
---
## Features Summary

- 4-Week personalized planner
- Research assistant with curated explanations
- AI-driven code generation + reasoning
- Feedback agent for improvement suggestions
- Mock interview simulator with scoring + DB-backed history
- Shared context memory across agents
- Fully containerized deployment (Docker + Render)
- Secure: no secrets committed, environment-based config
---
## Author:
**Aditi Jha**
**LinkedIn**: https://www.linkedin.com/in/aditi-jha-ab8309305/



