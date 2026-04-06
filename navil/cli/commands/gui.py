"""Desktop GUI command handlers."""

from __future__ import annotations

import typer


def register(app: typer.Typer) -> None:
    @app.command("gui")
    def gui_command() -> None:
        """Launch Navil desktop GUI (PyQt6)."""
        from navil.gui.app import run_gui

        raise typer.Exit(code=run_gui())
