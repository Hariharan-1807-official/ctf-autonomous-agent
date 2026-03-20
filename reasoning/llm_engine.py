import os
import re
from openai import OpenAI
from utils.logger import logger


class LLMEngine:

    def __init__(self, tool_registry):

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")


        # ✅ Groq API (FAST + FREE TIER)
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )

        self.tools = tool_registry

    def _build_tools_prompt(self):

        tool_descriptions = []

        for name, tool in self.tools.tools.items():
            tool_descriptions.append(f"{name}: {tool.description}")

        return "\n".join(tool_descriptions)

    def decide(self, state, memory_context: str):

        tools_prompt = self._build_tools_prompt()

        prompt = f"""
You are an autonomous CTF agent.

GOAL:
Find either:
- flag{{...}}
- OR Bandit passwords

CURRENT STATE:
Step: {state.step}
Directory: {state.cwd}

RECENT OBSERVATIONS:
{memory_context[-1000:] if memory_context else "None"}

MISSION LOGIC:
- If you find a password → STOP
- If no new useful info → STOP
- Avoid repeating same action
- Prefer new exploration

AVAILABLE TOOLS:
{tools_prompt}

Respond in ONE format ONLY:

1. Continue:
TOOL: tool_name
ARGS: argument

2. Finish:
MISSION_COMPLETE
"""

        try:

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            text = response.choices[0].message.content

            logger.info(f"\nLLM OUTPUT:\n{text}")

            # ✅ TERMINATION CHECK
            if re.search(r"MISSION_COMPLETE", text, re.IGNORECASE):
                logger.info("🎯 MISSION COMPLETE DETECTED")
                return None, None

            # ✅ TOOL PARSING
            tool_match = re.search(r"TOOL:\s*(\w+)", text, re.IGNORECASE)
            arg_match = re.search(r"ARGS:\s*(.+)", text, re.IGNORECASE)

            if not tool_match:
                logger.error("Invalid LLM output → fallback")
                return "list_directory", "."

            tool = tool_match.group(1)
            arg = arg_match.group(1).strip() if arg_match else "."

            return tool, arg

        except Exception as e:

            logger.error(f"LLM error: {e}")
            return "list_directory", "."