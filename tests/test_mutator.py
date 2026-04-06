from __future__ import annotations

from pathlib import Path

from navil.mutator.corpus import PayloadCorpus
from navil.mutator.engine import PayloadMutator


def test_mutator_generates_payloads(tmp_path: Path) -> None:
    corpus = PayloadCorpus(tmp_path)
    corpus.save("xss", ["<script>alert(1)</script>"])
    mutator = PayloadMutator(corpus)
    generated = mutator.generate("xss", limit=10)
    assert generated


def test_mutator_feedback_persists(tmp_path: Path) -> None:
    corpus = PayloadCorpus(tmp_path)
    corpus.save("sqli", ["' OR '1'='1"])
    mutator = PayloadMutator(corpus)
    mutator.feedback("sqli", ["\" OR \"1\"=\"1"])
    assert len(corpus.load("sqli")) >= 2
