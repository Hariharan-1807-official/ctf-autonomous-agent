import re
from configs.settings import settings
from tools.tool_registry import ToolRegistry
from reasoning.llm_engine import LLMEngine
from utils.logger import logger

PASSWORD_PATTERN = re.compile(r"[A-Za-z0-9]{32}")


class Controller:
    def __init__(self, state, runner):
        self.state = state
        self.tools = ToolRegistry(runner)
        self.llm = LLMEngine(self.tools)

    def run(self):
        logger.info("Controller started")

        ls_output = self.tools.get("list_directory").run(".")
        logger.info(f"📁 CURRENT CONTENTS:\n{ls_output}")
        self.state.add_observation(ls_output)
        self.state.cwd = "/home/bandit0"

        try:
            while self.state.step < settings.max_steps:

                logger.info(f"Step {self.state.step}")

                memory_context = "\n".join(self.state.observations[-2:])
                tool_name, arg = self.llm.decide(self.state, memory_context)

                if tool_name is None:
                    logger.info("🏆 AGENT COMPLETED MISSION")
                    break

                tool = self.tools.get(tool_name)
                if not tool:
                    logger.error(f"Invalid tool: {tool_name}")
                    break

                action_str = f"{tool_name} {arg}"
                output = tool.run(arg)

                logger.info(f"Action: {tool_name} {arg}")
                logger.info(f"Output:\n{output}")

                self.state.add_action(action_str)
                self.state.add_observation(output)
                self.state.increment_step()

                # ✅ Controller-level regex termination (the missing piece)
                match = PASSWORD_PATTERN.search(output)
                if match:
                    logger.info(f"🎯 PASSWORD FOUND: {match.group(0)}")
                    logger.info("🏆 MISSION COMPLETE (regex termination)")
                    break

                # Anti-loop
                recent_actions = self.state.actions[-3:]
                if len(recent_actions) >= 2 and recent_actions[-1] == recent_actions[-2]:
                    logger.warning("⚠️ Repeated action detected, stopping agent")
                    break

                if len(set(self.state.actions[-3:])) == 1:
                    logger.warning("⚠️ Agent is stuck in a loop, stopping agent")
                    break

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Crash: {e}")
        finally:
            logger.info("Controller finished execution")