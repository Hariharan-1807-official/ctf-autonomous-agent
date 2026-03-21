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

            # Password found
            match = PASSWORD_PATTERN.search(output)
            if match:
                password = match.group(0)
                logger.info(f"🎯 PASSWORD FOUND: {password}")
                self.state.save_password(self.state.current_level, password)
                return password

            # Anti-loop
            recent_actions = self.state.actions[-3:]
            if len(recent_actions) >= 3 and len(set(recent_actions)) == 1:
                logger.warning("⚠️ Loop detected, stopping level")
                return None

        logger.warning("⚠️ Max steps reached for this level")
        return None

    def run(self):
        logger.info("Controller started — Multi-level escalation")

        try:
            while self.state.current_level <= self.state.max_level:
                level = self.state.current_level
                username = f"bandit{level}"

                # Get password for this level
                if level == 0:
                    password = settings.ssh_password
                else:
                    password = self.state.passwords.get(level - 1)
                    if not password:
                        logger.error(f"No password for level {level}, stopping")
                        break

                # Connect as this level's user
                self.ssh_client.connect(
                    host=settings.ssh_host,
                    port=settings.ssh_port,
                    username=username,
                    password=password
                )

                # Solve this level
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