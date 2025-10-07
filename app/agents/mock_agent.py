# app/agents/mock_agent.py

import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI
from app.core.mcp import BaseAgent

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GENERATOR_PROMPT = """You are a seasoned technical interviewer.
Given a role and focus area, generate 5 concise interview questions.
Return ONLY JSON: {"questions": ["Q1", "Q2", "Q3", "Q4", "Q5"]}.
Questions should be specific and non-trivial.
"""

EVALUATOR_PROMPT = """You are an interviewer evaluating a single answer briefly.
Return ONLY JSON:
{
  "score": 1-5,
  "feedback": "<2-4 sentences constructive feedback>",
  "key_points": ["...", "..."]
}
Be concise and concrete.
"""


class MockInterviewAgent(BaseAgent):
    """Handles mock interview sessions and evaluations."""

    def start_session(self, role: str, focus: str) -> Dict[str, Any]:
        """Generate 5 interview questions for the given role and focus."""
        user_prompt = f"Role: {role}\nFocus: {focus}\nGenerate 5 questions."
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            messages=[
                {"role": "system", "content": GENERATOR_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        text = resp.choices[0].message.content.strip()
        try:
            data = json.loads(text)
            questions: List[str] = data.get("questions", [])
        except json.JSONDecodeError:
            questions = []

        session = {
            "role": role,
            "focus": focus,
            "questions": questions,
            "index": 0,
            "history": [],  # list of {q, a, eval}
        }

        self.update_context("mock_session", session)
        return session

    def evaluate_answer(self, answer: str) -> Dict[str, Any]:
        """Evaluate the candidate's answer to the current question."""
        session = self.get_context("mock_session", {})
        idx = session.get("index", 0)
        qs = session.get("questions", [])
        if idx >= len(qs):
            return {"done": True}

        q = qs[idx]
        user_prompt = f"Question:\n{q}\n\nCandidate answer:\n{answer}"

        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            messages=[
                {"role": "system", "content": EVALUATOR_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        text = resp.choices[0].message.content.strip()
        try:
            evaluation = json.loads(text)
        except json.JSONDecodeError:
            evaluation = {"score": 3, "feedback": text[:400], "key_points": []}

        # Update session state
        session["history"].append({"q": q, "a": answer, "eval": evaluation})
        session["index"] = idx + 1
        self.update_context("mock_session", session)

        return {
            "question": q,
            "evaluation": evaluation,
            "next_index": session["index"],
            "done": session["index"] >= len(qs),
        }

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic shim to satisfy BaseAgent.run() and dispatch to the correct action.

        input_data = {
          "action": "start" | "answer",
          "role": "...",      # required for action=start
          "focus": "...",     # required for action=start
          "answer": "..."     # required for action=answer
        }
        """
        action = (input_data or {}).get("action", "start")

        if action == "start":
            role = input_data.get("role", "")
            focus = input_data.get("focus", "")
            return self.start_session(role, focus)

        elif action == "answer":
            ans = input_data.get("answer", "")
            return self.evaluate_answer(ans)

        else:
            return {"error": f"Unknown action: {action}"}
