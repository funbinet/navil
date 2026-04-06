"""Typer CLI entrypoint."""

from __future__ import annotations

import typer

from navil.cli.commands import brain, config, gui, report, scan, scope
from navil.cli.display import banner

app = typer.Typer(help="Navil autonomous security scanner")

scan.register(app)
report.register(app)
brain.register(app)
config.register(app)
scope.register(app)
gui.register(app)


@app.callback()
def main() -> None:
    """Render banner once before command execution."""
    banner()
