"""Training utilities for the adaptive scan policy."""

from __future__ import annotations

from dataclasses import dataclass

from navil.brain.agent import AdaptiveRLAgent


@dataclass(slots=True)
class TrainingMetric:
    plugin_name: str
    reward: float
    source: str


class BrainTrainer:
    def __init__(self, agent: AdaptiveRLAgent) -> None:
        self.agent = agent

    def offline_pretrain(self, records: list[TrainingMetric]) -> None:
        for record in records:
            self.agent.update(record.plugin_name, record.reward, {"source": record.source})

    def online_update(self, plugin_rewards: dict[str, float], source: str = "scan") -> None:
        for plugin_name, reward in plugin_rewards.items():
            self.agent.update(plugin_name, reward, {"source": source})

    def status(self) -> dict[str, object]:
        snapshot = self.agent.snapshot()
        snapshot["trainer"] = "adaptive-epsilon-greedy"
        return snapshot
