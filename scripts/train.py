"""Offline pretraining utility for Navil brain."""

from __future__ import annotations

import argparse
from pathlib import Path

from navil.brain.agent import AdaptiveRLAgent
from navil.brain.trainer import BrainTrainer, TrainingMetric


def main() -> None:
    parser = argparse.ArgumentParser(description="Pretrain Navil adaptive brain")
    parser.add_argument("--model", default="models/brain.json", help="Path to brain model json")
    parser.add_argument("--rounds", type=int, default=200, help="Synthetic pretraining rounds")
    args = parser.parse_args()

    agent = AdaptiveRLAgent(Path(args.model))
    trainer = BrainTrainer(agent)

    records = []
    for _ in range(args.rounds):
        records.extend(
            [
                TrainingMetric("headers", 3.0, "offline"),
                TrainingMetric("cors", 4.0, "offline"),
                TrainingMetric("info_disclosure", 5.0, "offline"),
                TrainingMetric("xss", 6.0, "offline"),
                TrainingMetric("sqli", 6.5, "offline"),
            ]
        )

    trainer.offline_pretrain(records)
    agent.save()
    print(f"Saved model to {args.model}")


if __name__ == "__main__":
    main()
