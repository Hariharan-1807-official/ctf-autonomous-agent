from dataclasses import dataclass, field
from typing import List


@dataclass
class AgentState:

    step: int = 0
    cwd: str = "/"
    observations: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)

    def add_action(self, action: str):
        self.actions.append(action)

    def increment_step(self):
        self.step += 1

    def add_observation(self, observation: str):
        self.observations.append(observation)