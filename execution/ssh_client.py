import paramiko
from configs.settings import settings
from utils.logger import logger


class SSHClient:

    def __init__(self):
        self.client = None

    def connect(self):

        if self.client:
            return

        logger.info("Connecting to SSH server...")

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:

            self.client.connect(
                hostname=settings.ssh_host,
                port=settings.ssh_port,
                username=settings.ssh_user,
                password=settings.ssh_password,
                timeout=10
            )

            logger.info("SSH connection established")

        except Exception as e:

            logger.error(f"SSH connection failed: {e}")
            raise

    def execute(self, command: str, timeout: int = 10):

        try:

            stdin, stdout, stderr = self.client.exec_command(
                command,
                timeout=timeout
            )

            output = stdout.read().decode()
            error = stderr.read().decode()

            if error:
                return error

            return output

        except Exception as e:

            logger.error(f"Command execution failed: {e}")
            return str(e)

    def close(self):

        if self.client:
            self.client.close()
            logger.info("SSH connection closed")