"""Lightweight semantic similarity store used for local pattern recall."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import cast


@dataclass(slots=True)
class VectorItem:
    item_id: str
    text: str
    metadata: dict[str, str]
    vector: Counter[str]


class LocalVectorStore:
    def __init__(self) -> None:
        self._items: list[VectorItem] = []

    @staticmethod
    def _embed(text: str) -> Counter[str]:
        cleaned = "".join(char.lower() for char in text if char.isalnum() or char.isspace())
        return Counter(cleaned.split())

    @staticmethod
    def _cosine(a: Counter[str], b: Counter[str]) -> float:
        dot = sum(a[token] * b[token] for token in a.keys() & b.keys())
        norm_a = math.sqrt(sum(value * value for value in a.values()))
        norm_b = math.sqrt(sum(value * value for value in b.values()))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    async def add(self, item_id: str, text: str, metadata: dict[str, str] | None = None) -> None:
        self._items.append(
            VectorItem(
                item_id=item_id,
                text=text,
                metadata=metadata or {},
                vector=self._embed(text),
            )
        )

    async def similar(self, text: str, top_k: int = 5) -> list[dict[str, object]]:
        query = self._embed(text)
        scored = [
            {
                "item_id": item.item_id,
                "score": self._cosine(query, item.vector),
                "metadata": item.metadata,
                "text": item.text,
            }
            for item in self._items
        ]
        scored.sort(key=lambda item: cast(float, item["score"]), reverse=True)
        return scored[:top_k]
