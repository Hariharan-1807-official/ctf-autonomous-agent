import paramiko
from utils.logger import logger


class SSHClient:
    def __init__(self):
        self.client = None

    def connect(self, host, port, username, password):
        if self.client:
            self.client.close()

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        logger.info(f"Connecting as {username}...")
        self.client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=10
        )
        logger.info(f"SSH connected as {username}")

    def execute(self, command: str) -> str:
        stdin, stdout, stderr = self.client.exec_command(command, timeout=10)
        return stdout.read().decode() + stderr.read().decode()

    def close(self):
        if self.client:
            self.client.close()
            logger.info("SSH connection closed")