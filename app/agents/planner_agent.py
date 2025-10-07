# app/agents/planner_agent.py

import os
from openai import OpenAI
from app.core.mcp import BaseAgent
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class PlannerAgent(BaseAgent):
    def run(self, input_data):
        prompt = f"""
        You are an expert career coach. Break down the following interview goal into a 4-week plan with weekly objectives.

        Goal: {input_data}

        Format:
        Week 1: ...
        Week 2: ...
        Week 3: ...
        Week 4: ...
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        plan = response.choices[0].message.content
        self.update_context("interview_plan", plan)
        return plan
