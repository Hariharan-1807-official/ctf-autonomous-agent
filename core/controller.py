from utils.logger import logger
from core.state import AgentState
from configs.settings import settings


class Controller:

    def __init__(self):
        self.state = AgentState()

    def run(self):
        try:
            logger.info("Controller started")

            while not self.state.flag_found and self.state.step < settings.max_steps:

                logger.info(f"Step {self.state.step}")

                # Placeholder action (Phase-0 simulation)
                action = "ls"

                logger.info(f"Executing action: {action}")

                self.state.add_history(action)

                # Simulated output
                output = "file1 file2 file3"
                self.state.last_output = output
                self.state.add_observation(output)

                logger.info(f"Output: {output}")

                self.state.increment_step()

        except KeyboardInterrupt:
            logger.info("Execution stopped by user")

        except Exception as e:
            logger.error(f"System crash: {e}")

        finally:
            logger.info("Controller finished execution")