import re
from configs.settings import settings
from tools.tool_registry import ToolRegistry
from reasoning.llm_engine import LLMEngine
from utils.logger import logger

PASSWORD_PATTERN = re.compile(r"\b[A-Za-z0-9]{32,33}\b")


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

        # Initial scan
        ls_output = self.tools.get("list_directory").run(".")
        logger.info(f"📁 CURRENT CONTENTS:\n{ls_output}")
        self.state.add_observation(ls_output)
        self.state.cwd = f"/home/bandit{self.state.current_level}"

        while self.state.step < settings.max_steps:
            logger.info(f"Step {self.state.step}")
            recent_actions = self.state.actions[-4:]
            recent_observations = self.state.observations[-4:]
            pairs=[]
            for i,action in enumerate(recent_actions):
                pairs.append(f"ACTION: {action}")
                if i < len(recent_observations):
                    pairs.append(f"RESULT: {recent_observations[i]}")
            memory_context = "\n".join(pairs)
            tool_name, arg = self.llm.decide(self.state, memory_context)

            if tool_name is None:
                logger.info("🏆 LLM signals mission complete")
                return None

            tool = self.tools.get(tool_name)
            if not tool:
                logger.warning(f"Unknown tool: {tool_name}, trying run_command")
                tool = self.tools.get("run_command")
                arg = tool_name  # treat as raw command

            output = tool.run(arg)
            logger.info(f"Action: {tool_name} | Args: {arg}")
            logger.info(f"Output:\n{output}")

            self.state.add_action(f"{tool_name} {arg}")
            self.state.add_observation(output)
            self.state.increment_step()

            # Check for password
            match = PASSWORD_PATTERN.search(output)
            if match:
                password = match.group(0)
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
        logger.info("Controller started — Autonomous CTF Agent")

        try:
            while self.state.current_level <= self.state.max_level:
                level = self.state.current_level
                username = f"bandit{level}"
                password = settings.ssh_password if level == 0 else self.state.passwords.get(level - 1)

                if not password:
                    logger.error(f"No password for level {level}, stopping")
                    break

                self.ssh_client.connect(
                    host=settings.ssh_host,
                    port=settings.ssh_port,
                    username=username,
                    password=password
                )

                found = self.solve_level()

                if found:
                    logger.info(f"✅ Level {level} solved → {found}")
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
            for lvl, pwd in self.state.passwords.items():
                logger.info(f"  bandit{lvl} → bandit{lvl+1}: {pwd}")
            logger.info("Controller finished")