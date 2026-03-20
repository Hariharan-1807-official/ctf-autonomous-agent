from configs.settings import settings
from utils.logger import logger
from tools.tool_registry import ToolRegistry
from reasoning.llm_engine import LLMEngine


class Controller:

    def __init__(self, state, runner):

        self.state = state
        self.runner = runner

        self.tools = ToolRegistry(runner)
        self.llm = LLMEngine(self.tools)

    def run(self):

        logger.info("\nController started")

        try:

            while self.state.step < settings.max_steps:

                logger.info(f"\nStep {self.state.step}")

                # ✅ Reduced memory (avoid loops)
                memory_context = "\n".join(self.state.observations[-3:])

                tool_name, arg = self.llm.decide(self.state, memory_context)

                # ✅ TERMINATION
                if tool_name is None:
                    logger.info("🏆 AGENT ACHIEVED GOAL")
                    break

                tool = self.tools.get(tool_name)

                if not tool:
                    logger.error(f"Tool {tool_name} not found → fallback")
                    tool = self.tools.get("list_directory")
                    arg = "."

                output = tool.run(arg)

                self.state.add_observation(output)
                self.state.increment_step()

        except KeyboardInterrupt:
            logger.info("Interrupted by user")

        except Exception as e:
            logger.error(f"Controller crashed: {e}")

        finally:
            logger.info("Controller finished execution")