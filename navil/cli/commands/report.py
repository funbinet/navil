"""Report command handlers."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer

from navil.core.engine import NavilEngine
from navil.reporting.generator import ReportGenerator


def register(app: typer.Typer) -> None:
    @app.command("report")
    def report_command(
        scan_id: str = typer.Option(..., "--scan-id", help="Scan identifier"),
        fmt: str = typer.Option("html", "--format", help="json|html|md|pdf"),
        output: str | None = typer.Option(None, "--output", help="Output path"),
    ) -> None:
        async def _run() -> None:
            engine = NavilEngine()
            await engine.initialize()
            scan = await engine.get_scan(scan_id)
            if scan is None:
                raise typer.BadParameter("Unknown scan id")

            generator = ReportGenerator()
            path = await generator.generate(scan, fmt=fmt, output_path=Path(output) if output else None)
            typer.echo(f"Report generated at: {path}")

        asyncio.run(_run())
