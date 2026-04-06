"""Brain command handlers."""

from __future__ import annotations

import json

import typer

from navil.core.engine import NavilEngine


def register(app: typer.Typer) -> None:
    brain_app = typer.Typer(help="Adaptive brain commands")

    @brain_app.command("status")
    def status() -> None:
        engine = NavilEngine()
        snapshot = engine.brain_status()
        typer.echo(json.dumps(snapshot, indent=2))

    @brain_app.command("train")
    def train(episodes: int = typer.Option(100, "--episodes", min=1, max=10000)) -> None:
        engine = NavilEngine()
        rewards = {
            "headers": min(episodes / 100, 3.0),
            "cors": min(episodes / 120, 2.5),
            "info_disclosure": min(episodes / 80, 3.5),
        }
        engine.trainer.online_update(rewards, source="cli-synthetic")
        engine.brain.save()
        typer.echo("Brain update complete")

    app.add_typer(brain_app, name="brain")
