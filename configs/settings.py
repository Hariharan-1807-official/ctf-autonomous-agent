import os
from dataclasses import dataclass


@dataclass
class Settings:
    ssh_host: str = "bandit.labs.overthewire.org"
    ssh_port: int = 2220
    ssh_user: str = "bandit0"
    ssh_password: str = os.getenv("SSH_PASSWORD", "")

    max_steps: int = 50
    command_timeout: int = 10


settings = Settings()