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
        # ✅ Extract passwords (core Phase-4 feature)
        passwords = re.findall(r"[A-Za-z0-9]{32}", memory_context)
        if passwords:
            logger.info(f"🔑 Passwords found: {passwords[0]}")
            return None, None  # Signal mission complete

        tools_list = "\n".join([
            f"{name}: {tool.description}"
            for name, tool in self.tools.tools.items()
        ])

        prompt = f"""
🎯 MISSION: Extract bandit0 password from home/bandit0/readme

CURRENT PATH: {state.cwd}

CRITICAL PATHS (relative from current dir):
1. list_directory bandit0    (if in /home)
2. read_file readme          (if in home/bandit0) 
3. 32-char password → MISSION_COMPLETE

FOUND PASSWORDS: {', '.join(passwords) if passwords else 'None'}

RECENT OBSERVATIONS:
{state.observations[-2:]}

RULES:
- Use RELATIVE PATHS from current directory
- From /home → list_directory bandit0
- From home/bandit0 → read_file readme
- NEVER use absolute paths

TOOLS:
{tools_list}

FORMAT:
TOOL: list_directory
ARGS: bandit0

OR
TOOL: read_file  
ARGS: readme

OR
MISSION_COMPLETE
"""


        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.choices[0].message.content

            # ✅ TERMINATION FIRST (IMPORTANT)
            if "MISSION_COMPLETE" in text.upper():
                logger.info("🎯 MISSION COMPLETE DETECTED")
                return None, None

            # ✅ Robust parsing
            tool_match = re.search(r"TOOL:\s*(\w+)", text, re.IGNORECASE)
            arg_match = re.search(r"ARGS:\s*(.+)", text, re.IGNORECASE)

            if tool_match:
                tool = tool_match.group(1).strip()
                arg = arg_match.group(1).strip() if arg_match else "."
                return tool, arg

            # ✅ Fallback
            return "list_directory", "."

        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return "list_directory", "."