"""Adaptive policy agent for plugin prioritization."""

from __future__ import annotations

import json
import random
from pathlib import Path

from navil.brain.memory import Experience, PrioritizedReplayBuffer


class AdaptiveRLAgent:
    """A lightweight epsilon-greedy agent used for plugin ordering."""

    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path
        self.epsilon = 0.25
        self.epsilon_decay = 0.995
        self.epsilon_floor = 0.05
        self.learning_rate = 0.2
        self.plugin_scores: dict[str, float] = {}
        self.buffer = PrioritizedReplayBuffer()

    def choose_plugin_order(self, plugin_names: list[str]) -> list[str]:
        for name in plugin_names:
            self.plugin_scores.setdefault(name, 0.0)

        if random.random() < self.epsilon:
            shuffled = plugin_names[:]
            random.shuffle(shuffled)
            return shuffled

        return sorted(plugin_names, key=lambda name: self.plugin_scores[name], reverse=True)

    def update(self, plugin_name: str, reward: float, metadata: dict[str, str] | None = None) -> None:
        current = self.plugin_scores.get(plugin_name, 0.0)
        self.plugin_scores[plugin_name] = current + self.learning_rate * (reward - current)
        self.buffer.add(Experience(plugin_name=plugin_name, reward=reward, metadata=metadata or {}))
        self.epsilon = max(self.epsilon_floor, self.epsilon * self.epsilon_decay)

    def snapshot(self) -> dict[str, object]:
        return {
            "epsilon": self.epsilon,
            "plugin_scores": self.plugin_scores,
            "top_patterns": self.buffer.top_patterns(),
        }

    def save(self) -> None:
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        self.model_path.write_text(json.dumps(self.snapshot(), indent=2), encoding="utf-8")

    def load(self) -> None:
        if not self.model_path.exists():
            return
        payload = json.loads(self.model_path.read_text(encoding="utf-8"))
        self.epsilon = float(payload.get("epsilon", self.epsilon))
        raw_scores = payload.get("plugin_scores", {})
        if isinstance(raw_scores, dict):
            self.plugin_scores = {str(k): float(v) for k, v in raw_scores.items()}
