from configs.settings import settings
from utils.logger import logger
from core.state import AgentState
from tools.tool_registry import ToolRegistry


class Controller:

    def __init__(self, state: AgentState, runner):

        self.state = state
        self.runner = runner
        self.tools = ToolRegistry(runner)

    def run(self):

        logger.info("\nController started")

        while self.state.step < settings.max_steps:

            logger.info(f"\nStep {self.state.step}")

            tool = self.tools.get("list_directory")

            output = tool.run(self.state.cwd)

            self.state.add_observation(output)

            self.state.increment_step()

        logger.info("Controller finished execution")