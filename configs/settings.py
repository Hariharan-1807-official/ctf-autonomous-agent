import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class Settings:

    ssh_host: str = os.getenv("SSH_HOST", "localhost")
    ssh_port: int = int(os.getenv("SSH_PORT", "22"))
    ssh_user: str = os.getenv("SSH_USER", "")
    ssh_password: str = os.getenv("SSH_PASSWORD", "")

    max_steps: int = int(os.getenv("MAX_STEPS", "50"))


settings = Settings()