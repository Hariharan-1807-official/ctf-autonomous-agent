import os
from dataclasses import dataclass

@dataclass
class Settings:
    ssh_host: str = os.getenv("SSH_HOST", "bandit.labs.overthewire.org")
    ssh_port: int = int(os.getenv("SSH_PORT", "2220"))
    ssh_user: str = os.getenv("SSH_USER", "bandit0")
    ssh_password: str = os.getenv("SSH_PASSWORD", "bandit0")
    max_steps: int = int(os.getenv("MAX_STEPS", "20"))

settings = Settings()