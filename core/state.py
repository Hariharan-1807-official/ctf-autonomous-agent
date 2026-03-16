from dataclasses import dataclass, field
from typing import List


@dataclass
class AgentState:
    step: int = 0
    cwd: str = ""
    history: List[str] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    last_output: str = ""
    flag_found: bool = False

    def add_history(self, entry: str):
        self.history.append(entry)

    def add_observation(self, obs: str):
        self.observations.append(obs)

    def increment_step(self):
        self.step += 1