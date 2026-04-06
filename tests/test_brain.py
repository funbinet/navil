from __future__ import annotations

from pathlib import Path

from navil.brain.agent import AdaptiveRLAgent


def test_brain_updates_scores(tmp_path: Path) -> None:
    model = tmp_path / "brain.json"
    agent = AdaptiveRLAgent(model)
    order_before = agent.choose_plugin_order(["xss", "sqli", "headers"])
    agent.update("xss", 9.0)
    order_after = agent.choose_plugin_order(["xss", "sqli", "headers"])
    assert order_before
    assert order_after[0] == "xss"
