"""Scope command handlers."""

from __future__ import annotations

import json

import typer

from navil.config import dump_scope, load_scope


def register(app: typer.Typer) -> None:
    scope_app = typer.Typer(help="Scope management")

    @scope_app.command("validate")
    def validate(path: str = typer.Argument(".navil-scope.yml")) -> None:
        scope = load_scope(path)
        typer.echo(json.dumps(dump_scope(scope), indent=2))

    app.add_typer(scope_app, name="scope")
