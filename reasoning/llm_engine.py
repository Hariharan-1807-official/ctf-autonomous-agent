import os
import re
from openai import OpenAI
from utils.logger import logger


class LLMEngine:
    def __init__(self, tools):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("❌ GROQ_API_KEY not found")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.tools = tools

    def decide(self, state, memory_context: str):
        passwords = re.findall(r"[A-Za-z0-9]{32}", memory_context)

        tools_list = "\n".join([
            f"{name}: {tool.description}"
            for name, tool in self.tools.tools.items()
        ])

        prompt = f"""
You are solving Bandit Level {state.current_level} on OverTheWire.

CURRENT LEVEL: bandit{state.current_level}
CURRENT DIRECTORY: {state.cwd}

DIRECTORY CONTENTS (initial scan):
{state.observations[0] if state.observations else "Unknown"}

RECENT ACTIONS AND RESULTS:
{memory_context}

FOUND PASSWORDS SO FAR: {passwords if passwords else "None"}

BANDIT-SPECIFIC KNOWLEDGE:
- Level 0: password is in "readme"
- Level 1: password is in file named "-" → use read_file with arg "-"
- Level 2: password is in file with spaces → pass full filename including spaces
- Level 3: password is in hidden file inside "inhere/" directory → use read_file inhere/...Hiding-From-You
- Files named "-" are handled automatically with ./ prefix
- If you see a file inside a subdirectory, pass the FULL PATH like: inhere/filename

STRICT RULES:
- After listing a directory and seeing a file → immediately read that file
- Pass the FULL PATH to read_file including subdirectory e.g. inhere/...Hiding-From-You
- If you already found a 32-char password → MISSION_COMPLETE
- Do NOT repeat the same action twice

AVAILABLE TOOLS:
{tools_list}

Respond in ONE format only:

TOOL: tool_name
ARGS: argument

OR if password already found:

MISSION_COMPLETE
"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.choices[0].message.content
            logger.info(f"LLM: {text.strip()}")

            if "MISSION_COMPLETE" in text.upper():
                logger.info("🎯 MISSION COMPLETE (LLM signal)")
                return None, None

            tool_match = re.search(r"TOOL:\s*(\w+)", text, re.IGNORECASE)
            arg_match = re.search(r"ARGS:\s*(.+)", text, re.IGNORECASE)

            if tool_match:
                tool = tool_match.group(1).strip()
                arg = arg_match.group(1).strip() if arg_match else "."
                return tool, arg

            return "list_directory", "."

        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return "list_directory", "."