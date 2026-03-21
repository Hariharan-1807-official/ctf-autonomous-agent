from dataclasses import dataclass, field
from typing import List

@dataclass
class AgentState:
    step: int = 0
    cwd: str = "."
    current_level: int = 0
    max_level: int = 33
    passwords: dict = field(default_factory=dict)
    observations: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)

    def add_observation(self, obs: str):
        self.observations.append(obs)

    def add_action(self, action: str):
        self.actions.append(action)

    def increment_step(self):
        self.step += 1

    def save_password(self, level: int, password: str):
        self.passwords[level] = password

    def reset_for_next_level(self):
        self.step = 0
        self.cwd = "."
        self.observations = []
        self.actions = []
        self.current_level += 1