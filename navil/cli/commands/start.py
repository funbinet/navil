"""Interactive menu-driven shell command handlers."""

from __future__ import annotations

import typer

from navil.cli.menu_shell import NavilMenuShell


def register(app: typer.Typer) -> None:
    @app.command("start")
    def start_command() -> None:
        """Launch the interactive menu-driven CLI shell."""
        NavilMenuShell().run()
