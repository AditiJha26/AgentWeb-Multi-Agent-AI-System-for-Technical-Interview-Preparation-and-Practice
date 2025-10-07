# app/agents/coding_agent.py

import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

from app.core.mcp import BaseAgent

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a senior interview mentor who writes correct, clean code and clear explanations.
Given a problem statement and (optionally) a target language, produce a structured solution.

Return ONLY valid JSON with this schema:
{
  "language": "python | java | cpp | javascript | go | ...",
  "solution_code": "<full code>",
  "explanation": "<step-by-step reasoning for the approach>",
  "complexity": {
    "time": "e.g., O(n log n)",
    "space": "e.g., O(1)"
  }
}

Guidelines:
- Prefer idiomatic solutions.
- Include helpful function signatures.
- Do not include markdown fences in the JSON.
- If language not specified, default to 'python'."""

class CodingAgent(BaseAgent):
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        input_data = {
            "problem": "...",
            "language": "python"  # optional
        }
        """
        problem = input_data.get("problem", "").strip()
        lang = input_data.get("language", "").strip().lower()

        if not problem:
            raise ValueError("CodingAgent requires 'problem' text.")

        user_prompt = f"Problem:\n{problem}\n\nPreferred language: {lang or 'python'}"

        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",   # upgrade to gpt-4 if you want better quality
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
            # fallback: wrap in minimal structure
            data = {
                "language": lang or "python",
                "solution_code": text,
                "explanation": "Model returned non-JSON output; showing raw content.",
                "complexity": {"time": "N/A", "space": "N/A"}
            }

        # Save to shared context for convenience
        self.update_context("last_solution", data)
        return data
