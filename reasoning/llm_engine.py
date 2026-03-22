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
        passwords = re.findall(r"\b[A-Za-z0-9]{32,33}\b", memory_context)

        tools_list = "\n".join([
            f"- {name}: {tool.description}"
            for name, tool in self.tools.tools.items()
        ])

        prompt = f"""
You are an autonomous CTF security agent. You think like an experienced hacker and solve challenges by reasoning from what you observe.

CURRENT LEVEL: bandit{state.current_level}
CURRENT DIRECTORY: {state.cwd}

INITIAL DIRECTORY SCAN:
{state.observations[0] if state.observations else "Not yet scanned"}

RECENT ACTIONS AND OUTPUTS:
{memory_context}

PASSWORDS FOUND SO FAR: {passwords if passwords else "None"}

AVAILABLE TOOLS:
{tools_list}

CTF REASONING PRINCIPLES:
- Always start by understanding what is in the current environment
- If the home directory has only standard files (.bashrc, .bash_logout, .profile), the password file is elsewhere — use find_by_properties or run_command with find / and ownership/size filters
- When you see many subdirectories to search, use find_by_properties with size and readable filters rather than exploring each directory manually — e.g. 'inhere -readable -not -executable -size 1033c' finds the right file efficiently
- Files with unusual names (dash, spaces, dots) still contain data — read them with appropriate paths
- When many files exist, use check_file_type to identify human-readable ones
- Ownership matters — a file owned by the next level user is likely the target
- When you already have a file path from a previous action result, READ THAT FILE immediately
- If you already found a 32 or 33 character alphanumeric string, respond MISSION_COMPLETE
- Never repeat an action you already performed — act on what you found
- If reading a file returns binary content, skip it and try other files

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