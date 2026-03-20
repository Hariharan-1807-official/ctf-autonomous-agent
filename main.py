from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))
from utils.logger import logger
from core.state import AgentState
from core.controller import Controller
from execution.command_runner import CommandRunner
from execution.ssh_client import SSHClient


def main():

    logger.info("Starting CTF Autonomous Agent")

    state = AgentState()

    # ✅ Create SSH client
    ssh_client = SSHClient()

    # ✅ Connect once (persistent connection)
    ssh_client.connect()

    # ✅ Inject into runner
    runner = CommandRunner(ssh_client)

    controller = Controller(state, runner)

    try:
        controller.run()
    finally:
        # ✅ Always close connection
        ssh_client.close()


if __name__ == "__main__":
    main()