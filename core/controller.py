import re
from configs.settings import settings
from tools.tool_registry import ToolRegistry
from reasoning.llm_engine import LLMEngine
from utils.logger import logger

PASSWORD_PATTERN = re.compile(r"[A-Za-z0-9]{32}")


class Controller:
    def __init__(self, state, ssh_client, runner):
        self.state = state
        self.ssh_client = ssh_client
        self.tools = ToolRegistry(runner)
        self.llm = LLMEngine(self.tools)

    def _extract_ascii_file(self, file_type_output: str):
        for line in file_type_output.splitlines():
            if "ASCII text" in line:
                path = line.split(":")[0].strip()
                return path
        return None

    def _try_read_password(self, path: str):
        """Try to read a file and return password if found."""
        read_tool = self.tools.get("read_file")
        output = read_tool.run(path)
        logger.info(f"Output:\n{output}")
        self.state.add_action(f"read_file {path}")
        self.state.add_observation(output)
        self.state.increment_step()
        match = PASSWORD_PATTERN.search(output)
        if match:
            return match.group(0)
        return None

    def _get_parent_dir(self, find_output: str):
        """Extract the parent directory from find output."""
        lines = [l.strip() for l in find_output.splitlines() if l.strip()]
        if lines:
            # e.g. inhere/-file02 → inhere
            parts = lines[0].split("/")
            if len(parts) > 1:
                return "/".join(parts[:-1])
        return "."

    def solve_level(self):
        logger.info(f"\n{'='*50}")
        logger.info(f"🎯 SOLVING LEVEL {self.state.current_level}")
        logger.info(f"{'='*50}")

        ls_output = self.tools.get("list_directory").run(".")
        logger.info(f"📁 CURRENT CONTENTS:\n{ls_output}")
        self.state.add_observation(ls_output)
        self.state.cwd = f"/home/bandit{self.state.current_level}"

        while self.state.step < settings.max_steps:
            logger.info(f"Step {self.state.step}")

            memory_context = "\n".join(self.state.observations[-2:])
            tool_name, arg = self.llm.decide(self.state, memory_context)

            if tool_name is None:
                logger.info("🏆 LLM signals mission complete")
                return None

            tool = self.tools.get(tool_name)
            if not tool:
                logger.error(f"Invalid tool: {tool_name} → fallback")
                tool = self.tools.get("list_directory")
                arg = "."

            action_str = f"{tool_name} {arg}"
            output = tool.run(arg)

            logger.info(f"Action: {tool_name} {arg}")
            logger.info(f"Output:\n{output}")

            self.state.add_action(action_str)
            self.state.add_observation(output)
            self.state.increment_step()

            # Direct password found
            match = PASSWORD_PATTERN.search(output)
            if match:
                password = match.group(0)
                logger.info(f"🎯 PASSWORD FOUND: {password}")
                self.state.save_password(self.state.current_level, password)
                return password

            # After find_files → automatically run check_file_type on the directory
            if tool_name == "find_files":
                parent_dir = self._get_parent_dir(output)
                logger.info(f"📂 Auto-checking file types in: {parent_dir}")
                check_tool = self.tools.get("check_file_type")
                check_output = check_tool.run(parent_dir)
                logger.info(f"File types:\n{check_output}")
                self.state.add_action(f"check_file_type {parent_dir}")
                self.state.add_observation(check_output)
                self.state.increment_step()

                ascii_path = self._extract_ascii_file(check_output)
                if ascii_path:
                    logger.info(f"📄 ASCII file found: {ascii_path} → reading")
                    password = self._try_read_password(ascii_path)
                    if password:
                        logger.info(f"🎯 PASSWORD FOUND: {password}")
                        self.state.save_password(self.state.current_level, password)
                        return password

            # After check_file_type → immediately read the ASCII file
            if tool_name == "check_file_type":
                ascii_path = self._extract_ascii_file(output)
                if ascii_path:
                    logger.info(f"📄 ASCII file found: {ascii_path} → reading")
                    password = self._try_read_password(ascii_path)
                    if password:
                        logger.info(f"🎯 PASSWORD FOUND: {password}")
                        self.state.save_password(self.state.current_level, password)
                        return password

            # Anti-loop
            recent = self.state.actions[-3:]
            if len(recent) >= 3 and len(set(recent)) == 1:
                logger.warning("⚠️ Loop detected, stopping level")
                return None

        logger.warning("⚠️ Max steps reached")
        return None

    def run(self):
        logger.info("Controller started — Multi-level escalation")

        try:
            while self.state.current_level <= self.state.max_level:
                level = self.state.current_level
                username = f"bandit{level}"

                if level == 0:
                    password = settings.ssh_password
                else:
                    password = self.state.passwords.get(level - 1)
                    if not password:
                        logger.error(f"No password for level {level}, stopping")
                        break

                self.ssh_client.connect(
                    host=settings.ssh_host,
                    port=settings.ssh_port,
                    username=username,
                    password=password
                )

                found_password = self.solve_level()

                if found_password:
                    logger.info(f"✅ Level {level} solved → password for level {level + 1}: {found_password}")
                    self.state.reset_for_next_level()
                else:
                    logger.error(f"❌ Could not solve level {level}, stopping")
                    break

        except KeyboardInterrupt:
            logger.info("Stopped by user")
        except Exception as e:
            logger.error(f"Crash: {e}")
        finally:
            self.ssh_client.close()
            logger.info("\n📊 PASSWORDS COLLECTED:")
            for level, pwd in self.state.passwords.items():
                logger.info(f"  bandit{level} → bandit{level+1}: {pwd}")
            logger.info("Controller finished")