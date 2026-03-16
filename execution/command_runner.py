from execution.ssh_client import SSHClient
from utils.logger import logger


class CommandRunner:

    def __init__(self, ssh_client: SSHClient):
        self.ssh = ssh_client

    def run(self, command: str):

        logger.info(f"\nExecuting command: {command}")

        output = self.ssh.execute(command)

        logger.info(output.strip())

        return output