"""Config command handlers."""

from __future__ import annotations

import json

import typer

from navil.config import AppConfig


def register(app: typer.Typer) -> None:
    @app.command("config")
    def show_config() -> None:
        config = AppConfig()
        typer.echo(json.dumps(config.model_dump(mode="json"), indent=2, default=str))
