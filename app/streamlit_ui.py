# app/streamlit_ui.py



# ---- path shim ----
import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# -------------------

import streamlit as st
from app.core.context_store import ContextStore
from app.core.storage import save_context, load_context

# Agents
from app.agents.planner_agent import PlannerAgent
from app.agents.research_agent import ResearchAgent
from app.agents.coding_agent import CodingAgent
from app.agents.feedback_agent import FeedbackAgent
from app.agents.plan_parser_agent import PlanParserAgent
from app.agents.mock_agent import MockInterviewAgent

from uuid import uuid4


from app.core.db import init_db, save_context_dict, load_context_dict, log_mock_turn, fetch_mock_history
 # ensures tables exist on start
init_db()

if "mock_session_id" not in st.session_state:
    st.session_state["mock_session_id"] = str(uuid4())


st.set_page_config(page_title="AgentWeb+ | Interview Assistant", layout="wide")
st.title("🧭 AgentWeb+ — Interview Assistant")

# Shared context across tabs
if "context" not in st.session_state:
    st.session_state["context"] = ContextStore()
context = st.session_state["context"]

# ---- Global controls: Save/Load session ----


with st.sidebar:
    st.header("Session (PostgreSQL)")
    if st.button("💾 Save session to DB"):
        save_context_dict(context.get_all())
        st.success("Saved session to PostgreSQL")
    if st.button("📂 Load session from DB"):
        data = load_context_dict()
        for k, v in data.items():
            context.set(k, v)
        st.success("Loaded session from PostgreSQL")


tab_plan, tab_research, tab_topics, tab_coding, tab_feedback, tab_mock = st.tabs(
    ["📅 Planner", "🔎 Research", "🧩 Topics", "💻 Coding", "✅ Feedback", "🎤 Mock Interview"]
)

# ---------------- Planner ----------------
with tab_plan:
    st.subheader("Interview Planner")
    user_goal = st.text_input("Goal", key="planner_goal", placeholder="e.g., ML internship at Amazon in 4 weeks")
    if st.button("Generate 4-Week Plan"):
        if not user_goal.strip():
            st.warning("Please enter a goal first.")
        else:
            planner = PlannerAgent(name="planner", context=context)
            with st.spinner("Generating your plan..."):
                plan = planner.run(user_goal)
            context.set("interview_plan", plan)
            st.success("Here's your 4-week plan:")
            st.text_area("Plan", plan, height=320, key="plan_output")

    stored_plan = context.get("interview_plan")
    if stored_plan:
        with st.expander("Show saved plan"):
            st.text_area("Plan", stored_plan, height=260)

# ---------------- Research ----------------
with tab_research:
    st.subheader("Topic Research")
    topic = st.text_input("Topic to research", key="research_topic", placeholder="e.g., binary trees")
    if st.button("Find Resources"):
        if not topic.strip():
            st.warning("Please enter a topic to research.")
        else:
            researcher = ResearchAgent(name="research", context=context)
            with st.spinner(f"Curating resources for: {topic}"):
                items = researcher.run(topic)
            st.success("Curated resources:")
            for i, r in enumerate(items, start=1):
                title = r.get("title", "Untitled")
                url = r.get("url", "")
                rtype = r.get("type", "")
                why = r.get("why", "")
                if url:
                    st.markdown(f"**{i}. [{title}]({url})** · _{rtype}_  \n{why}")
                else:
                    st.markdown(f"**{i}. {title}** · _{rtype}_  \n{why}")

# ---------------- Topics (from plan) ----------------
with tab_topics:
    st.subheader("Extract Topics from Your Plan")
    plan_text = context.get("interview_plan", "")
    if not plan_text:
        st.info("Generate a plan first in the Planner tab.")
    else:
        if st.button("Extract topics per week"):
            parser = PlanParserAgent(name="parser", context=context)
            with st.spinner("Parsing plan into weekly topics..."):
                data = parser.run(plan_text)
            st.success("Topics extracted. See below.")

        topics_by_week = context.get("topics_by_week", {})
        if topics_by_week:
            for w in topics_by_week.get("weeks", []):
                st.markdown(f"### Week {w.get('week')}")
                cols = st.columns(3)
                topics = w.get("topics", [])
                for i, t in enumerate(topics):
                    col = cols[i % 3]
                    if col.button(f"🔎 {t}", key=f"topicbtn_{w.get('week')}_{i}"):
                        # research the clicked topic
                        researcher = ResearchAgent(name="research", context=context)
                        with st.spinner(f"Curating resources for: {t}"):
                            items = researcher.run(t)
                        st.session_state[f"topics_last_{t}"] = items

                # show last results for each clicked topic
                for t in topics:
                    items = st.session_state.get(f"topics_last_{t}")
                    if items:
                        with st.expander(f"Resources: {t}"):
                            for j, r in enumerate(items, start=1):
                                title = r.get("title", "Untitled")
                                url = r.get("url", "")
                                rtype = r.get("type", "")
                                why = r.get("why", "")
                                if url:
                                    st.markdown(f"**{j}. [{title}]({url})** · _{rtype}_  \n{why}")
                                else:
                                    st.markdown(f"**{j}. {title}** · _{rtype}_  \n{why}")

# ---------------- Coding ----------------
with tab_coding:
    st.subheader("Coding Agent")
    problem = st.text_area("Problem statement", height=160, key="coding_problem",
                           placeholder="e.g., Given an array of integers, return indices of two numbers that add up to a target.")
    language = st.selectbox("Language", ["python", "java", "cpp", "javascript", "go"], index=0, key="coding_lang")
    if st.button("Solve Problem"):
        if not problem.strip():
            st.warning("Please enter a problem statement.")
        else:
            solver = CodingAgent(name="coding", context=context)
            with st.spinner("Generating solution..."):
                result = solver.run({"problem": problem, "language": language})
            st.success("Solution generated:")
            st.markdown(f"**Language:** {result.get('language','')}")
            st.code(result.get("solution_code", ""), language=result.get("language", "python"))
            st.markdown("**Explanation**")
            st.write(result.get("explanation", ""))
            comp = result.get("complexity", {})
            st.markdown(f"**Complexity:** Time — {comp.get('time','N/A')}, Space — {comp.get('space','N/A')}")
            context.set("last_problem", problem)
            context.set("last_solution", result)

# ---------------- Feedback ----------------
with tab_feedback:
    st.subheader("Code Feedback")
    fb_problem = st.text_area("Problem (optional)", height=120, value=context.get("last_problem") or "", key="feedback_problem")
    user_code = st.text_area("Your code", height=220, key="feedback_code", placeholder="Paste your solution here…")
    fb_lang = st.selectbox("Language", ["python", "java", "cpp", "javascript", "go"], index=0, key="feedback_lang")
    if st.button("Get Feedback"):
        if not user_code.strip():
            st.warning("Please paste your code first.")
        else:
            reviewer = FeedbackAgent(name="feedback", context=context)
            with st.spinner("Reviewing your code..."):
                fb = reviewer.run({"problem": fb_problem, "code": user_code, "language": fb_lang})
            st.success(f"Score: {fb.get('score', 'N/A')} / 5")
            st.markdown("**Summary**")
            st.write(fb.get("summary", ""))
            cols = st.columns(3)
            with cols[0]:
                st.markdown("**Strengths**")
                for s in fb.get("strengths", []): st.write(f"- {s}")
            with cols[1]:
                st.markdown("**Improvements**")
                for s in fb.get("improvements", []): st.write(f"- {s}")
            with cols[2]:
                st.markdown("**Potential Bugs**")
                for s in fb.get("potential_bugs", []): st.write(f"- {s}")


# ---------------- Mock Interview ----------------
with tab_mock:
    st.subheader("Mock Interview")

    # Simple per-user session id (persists in this browser session)
    session_id = st.session_state["mock_session_id"]

    role = st.text_input("Role (e.g., SWE L3, Data Scientist, ML Engineer)", key="mock_role")
    focus = st.text_input("Focus area (e.g., data structures, system design, ML)", key="mock_focus")

    colA, colB = st.columns([1, 1])
    if colA.button("Start Session", key="mock_start_btn"):
        if not role.strip() or not focus.strip():
            st.warning("Please provide both role and focus.")
        else:
            mock = MockInterviewAgent(name="mock", context=context)
            with st.spinner("Generating questions..."):
                session = mock.start_session(role, focus)
            st.success("Session started.")

    session = context.get("mock_session", {}) or {}
    questions = session.get("questions", [])
    idx = session.get("index", 0)

    if questions:
        if idx < len(questions):
            st.markdown(f"**Question {idx+1}/{len(questions)}**")
            st.write(questions[idx])

            answer = st.text_area("Your answer", key=f"mock_answer_{idx}", height=160)

            if st.button("Submit answer", key=f"mock_submit_{idx}"):
                mock = MockInterviewAgent(name="mock", context=context)
                with st.spinner("Evaluating your answer..."):
                    res = mock.evaluate_answer(answer)

                # Guard if the agent returned 'done'
                if res.get("done"):
                    st.info("Session finished.")
                else:
                    st.success(f"Score: {res['evaluation'].get('score', 'N/A')} / 5")
                    st.write(res['evaluation'].get("feedback", ""))

                    # Persist this turn to PostgreSQL
                    try:
                        log_mock_turn(
                            session_id=session_id,
                            question=res.get("question", ""),
                            answer=answer,
                            evaluation=res.get("evaluation", {}),
                        )
                    except Exception as e:
                        st.warning(f"Could not log mock turn: {e}")

                    kp = res['evaluation'].get("key_points", [])
                    if kp:
                        with st.expander("Key points"):
                            for p in kp:
                                st.write(f"- {p}")
        else:
            st.success("✅ Session complete! See your history below.")

        # In-memory history
        history = session.get("history", [])
        if history:
            with st.expander("Interview History (in-memory)"):
                for i, h in enumerate(history, start=1):
                    st.markdown(f"**Q{i}:** {h['q']}")
                    st.markdown(f"**Your answer:** {h['a']}")
                    ev = h['eval']
                    st.markdown(f"**Score:** {ev.get('score','N/A')}/5")
                    st.markdown(f"**Feedback:** {ev.get('feedback','')}")

        # DB-backed history
        with st.expander("DB-backed History (from PostgreSQL)"):
            try:
                rows = fetch_mock_history(session_id=session_id)
                if not rows:
                    st.caption("No turns logged yet.")
                for r in rows:
                    st.markdown(f"- **Q:** {r['question']}")
                    st.markdown(f"  **A:** {r['answer']}")
                    st.markdown(
                        f"  **Score:** {r['evaluation'].get('score','N/A')} | "
                        f"**When:** {r['created_at']}"
                    )
            except Exception as e:
                st.warning(f"Could not load DB history: {e}")
    else:
        st.info("Click **Start Session** to generate interview questions.")
