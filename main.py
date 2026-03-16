from core.state import AgentState
from core.controller import Controller
from execution.ssh_client import SSHClient
from execution.command_runner import CommandRunner
from utils.logger import logger


def main():

    logger.info("\nStarting CTF Autonomous Agent\n")

    state = AgentState()

    ssh = SSHClient()
    ssh.connect()

    runner = CommandRunner(ssh)

    controller = Controller(state, runner)

    controller.run()

    ssh.close()


if __name__ == "__main__":
    main()