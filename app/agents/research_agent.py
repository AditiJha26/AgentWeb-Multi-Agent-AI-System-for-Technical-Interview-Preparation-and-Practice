# app/agents/research_agent.py

import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

from app.core.mcp import BaseAgent

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RESEARCH_SYSTEM_PROMPT = """You are a precise research assistant.
Given a technical topic, return a curated list of the best learning resources.
Prefer authoritative sources (official docs, top tutorials, reputable blogs, practice platforms).
Return a concise JSON object with a 'resources' array.
Each resource must have: title, url, type (doc|tutorial|practice|video|paper), and why (1-2 bullet points as a single string).
Keep results high quality, current, and non-duplicative. Do not include paywalled links when a free equivalent exists."""

class ResearchAgent(BaseAgent):
    """
    ResearchAgent collects high-quality resources for a given topic.
    It uses the OpenAI chat API to curate a structured list of sources.
    """

    def run(self, topic: str) -> List[Dict[str, Any]]:
        user_prompt = f"Topic: {topic}\nReturn exactly 5–7 items."

        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",  # economical; swap to gpt-4 for higher quality
            temperature=0.2,
            messages=[
                {"role": "system", "content": RESEARCH_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ]
        )

        text = resp.choices[0].message.content.strip()

        # Try to parse JSON; if it fails, wrap as a single note.
        data = {"resources": []}
        try:
            data = json.loads(text)
            resources = data.get("resources", [])
        except json.JSONDecodeError:
            resources = [{
                "title": f"Suggested reading for: {topic}",
                "url": "",
                "type": "note",
                "why": text[:1000]
            }]

        # Persist into shared context for other agents / UI
        key = f"resources::{topic.lower()}"
        self.update_context(key, resources)

        # Also keep a simple "last_resources" pointer
        self.update_context("last_resources", {"topic": topic, "items": resources})

        return resources
