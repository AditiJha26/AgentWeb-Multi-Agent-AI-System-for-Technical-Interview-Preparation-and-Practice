# app/agents/feedback_agent.py

import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

from app.core.mcp import BaseAgent

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a strict but constructive interviewer.
Grade the candidate's code for correctness, clarity, efficiency, and edge cases.

Return ONLY JSON like:
{
  "score": 1-5,
  "summary": "<overall assessment in 2-4 sentences>",
  "strengths": ["...", "..."],
  "improvements": ["...", "..."],
  "potential_bugs": ["...", "..."]
}"""

class FeedbackAgent(BaseAgent):
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        input_data = {
            "problem": "...",
            "code": "...",
            "language": "python"
        }
        """
        problem = input_data.get("problem", "").strip()
        code = input_data.get("code", "").strip()
        language = input_data.get("language", "python")

        if not code:
            raise ValueError("FeedbackAgent requires 'code'.")

        user_prompt = f"Problem:\n{problem}\n\nLanguage: {language}\n\nCandidate's code:\n{code}"

        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )

        text = resp.choices[0].message.content.strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = {
                "score": 3,
                "summary": text[:400],
                "strengths": [],
                "improvements": ["Return was not valid JSON; displaying raw text."],
                "potential_bugs": []
            }

        # Save last feedback in context
        self.update_context("last_feedback", data)
        return data
