# llm_client.py (Groq native version)

import os
import json
import re
from dotenv import load_dotenv
from groq import Groq
from llm_tools import TOOLS

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in environment or .env file")

class LLMClient:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)

    def extract_json(self, text):
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in LLM response")
        return match.group(0)

    def process(self, user_input, document_context=""):
        """
        자연어 → Groq → JSON tool call 반환
        """

        system_prompt = f"""
You are an editor control AI.

Available tools:
{json.dumps(TOOLS, indent=2)}

You MUST respond ONLY in valid JSON.
Do not explain.
Do not use markdown.
Do not add text before or after JSON.

If a tool is required:

{{
  "action": "tool_name",
  "parameters": {{ ... }}
}}

Current document:
{document_context}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        json_str = self.extract_json(content)
        return json.loads(json_str)