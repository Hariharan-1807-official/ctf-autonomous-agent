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
            f"- {name}: {tool.description}"
            for name, tool in self.tools.tools.items()
        ])

        prompt = f"""
You are an autonomous Linux CTF agent solving OverTheWire Bandit challenges.

CURRENT LEVEL: bandit{state.current_level}
CURRENT DIRECTORY: {state.cwd}

INITIAL DIRECTORY SCAN:
{state.observations[0] if state.observations else "Not yet scanned"}

RECENT ACTIONS AND OUTPUTS:
{memory_context}

FOUND PASSWORDS: {passwords if passwords else "None yet"}

AVAILABLE TOOLS:
{tools_list}

GENERAL STRATEGY:
- Observe what files and directories exist
- If you see a directory → explore it
- If you see files → determine which ones might contain a password
- If there are many files of unknown type → use check_file_type to identify the readable one
- If a file contains a 32-character alphanumeric string → that is the password
- Use the full path when reading files inside subdirectories e.g. inhere/filename
- Files with special names like "-" or names starting with "--" are handled automatically
- Never repeat an action you already performed
- If you have already found a 32-character password → respond MISSION_COMPLETE

Respond in ONE format only:

TOOL: tool_name
ARGS: argument

OR:

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