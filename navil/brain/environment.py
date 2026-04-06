"""Environment adapter for scan episodes."""

from __future__ import annotations

from dataclasses import dataclass

from navil.brain.state import ScanState


@dataclass(slots=True)
class EnvironmentStep:
    state: ScanState
    action: str
    reward: float
    done: bool


class ScanEnvironment:
    def __init__(self) -> None:
        self.steps: list[EnvironmentStep] = []

    def record(self, state: ScanState, action: str, reward: float, done: bool) -> None:
        self.steps.append(EnvironmentStep(state=state, action=action, reward=reward, done=done))

    def total_reward(self) -> float:
        return sum(step.reward for step in self.steps)
