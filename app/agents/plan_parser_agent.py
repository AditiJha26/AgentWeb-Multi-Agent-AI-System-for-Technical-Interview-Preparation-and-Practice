# app/agents/plan_parser_agent.py

import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI
from app.core.mcp import BaseAgent

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a precise syllabus parser.
Input: a 4-week interview prep plan in free text.
Output: JSON with an array 'weeks', each item: {"week": 1..n, "topics": ["topic1", "topic2", ...]}.
- Extract only concrete study topics (e.g., 'binary trees', 'DP', 'probability basics', 'SQL window functions', 'REST vs RPC', 'system design: load balancers').
- 3–7 topics per week.
- Lowercase topics.
Return ONLY valid JSON with keys: weeks.
"""

class PlanParserAgent(BaseAgent):
    def run(self, plan_text: str) -> Dict[str, Any]:
        if not plan_text or not plan_text.strip():
            raise ValueError("PlanParserAgent requires non-empty plan text.")

        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": plan_text}
            ],
        )

        text = resp.choices[0].message.content.strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = {"weeks": []}

        self.update_context("topics_by_week", data)
        # Also flatten topics
        flat = []
        for w in data.get("weeks", []):
            flat.extend(w.get("topics", []))
        self.update_context("topics_flat", list(dict.fromkeys(flat)))  # unique preserve order
        return data
