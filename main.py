from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

from utils.logger import logger
from core.state import AgentState
from core.controller import Controller
from execution.ssh_client import SSHClient
from execution.command_runner import CommandRunner


def main():
    logger.info("Starting CTF Autonomous Agent — Phase 5")

    state = AgentState()
    ssh_client = SSHClient()
    runner = CommandRunner(ssh_client)

    controller = Controller(state, ssh_client, runner)
    controller.run()


if __name__ == "__main__":
    main()