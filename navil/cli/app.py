"""Typer CLI entrypoint."""

from __future__ import annotations

import typer

from navil.cli.commands import brain, config, report, scan, scope, start
from navil.cli.display import banner
from navil.cli.menu_shell import NavilMenuShell

app = typer.Typer(help="Navil autonomous security scanner", invoke_without_command=True)

scan.register(app)
report.register(app)
brain.register(app)
config.register(app)
scope.register(app)
start.register(app)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Render banner once before command execution."""
    banner()
    if ctx.invoked_subcommand is None:
        NavilMenuShell().run()
