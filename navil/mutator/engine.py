"""Mutation orchestrator combining corpus and genetic strategies."""

from __future__ import annotations

from navil.mutator.corpus import PayloadCorpus
from navil.mutator.encoder import stack
from navil.mutator.genetic import evolve


class PayloadMutator:
    def __init__(self, corpus: PayloadCorpus | None = None) -> None:
        self.corpus = corpus or PayloadCorpus()

    def generate(self, category: str, *, limit: int = 50) -> list[str]:
        base_payloads = self.corpus.load(category)
        if not base_payloads:
            return []

        encoded = [
            stack(payload, ["url"])
            for payload in base_payloads[: min(20, len(base_payloads))]
        ]
        evolved = evolve(base_payloads + encoded, {payload: 1.0 for payload in base_payloads}, rounds=2)
        return evolved[:limit]

    def feedback(self, category: str, successful_payloads: list[str]) -> None:
        existing = self.corpus.load(category)
        self.corpus.save(category, existing + successful_payloads)
