"""Experience replay and pattern extraction."""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass


@dataclass(slots=True)
class Experience:
    plugin_name: str
    reward: float
    metadata: dict[str, str]


class PrioritizedReplayBuffer:
    def __init__(self, capacity: int = 5000) -> None:
        self.capacity = capacity
        self._buffer: list[Experience] = []

    def add(self, experience: Experience) -> None:
        if len(self._buffer) >= self.capacity:
            self._buffer.pop(0)
        self._buffer.append(experience)

    def sample(self, batch_size: int = 64) -> list[Experience]:
        if not self._buffer:
            return []
        k = min(batch_size, len(self._buffer))
        weighted = [max(item.reward, 0.1) for item in self._buffer]
        return random.choices(self._buffer, weights=weighted, k=k)

    def top_patterns(self, top_n: int = 5) -> list[tuple[str, float]]:
        totals: defaultdict[str, float] = defaultdict(float)
        counts: defaultdict[str, int] = defaultdict(int)
        for item in self._buffer:
            totals[item.plugin_name] += item.reward
            counts[item.plugin_name] += 1
        averaged = [(name, totals[name] / counts[name]) for name in counts]
        averaged.sort(key=lambda pair: pair[1], reverse=True)
        return averaged[:top_n]
