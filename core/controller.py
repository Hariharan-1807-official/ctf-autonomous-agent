from configs.settings import settings
from utils.logger import logger
from core.state import AgentState


class Controller:

    def __init__(self, state: AgentState, runner):

        self.state = state
        self.runner = runner

    def run(self):

        logger.info("\nController started")

        try:

            while self.state.step < settings.max_steps:

                logger.info(f"\nStep: {self.state.step}")

                action = f"ls -la {self.state.cwd}"

                output = self.runner.run(action)

                self.state.add_observation(output)

                self.state.increment_step()

        except KeyboardInterrupt:

            logger.info("Execution interrupted")

        except Exception as e:

            logger.error(f"Controller crashed: {e}")

        finally:

            logger.info("Controller finished execution")