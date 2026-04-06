"""Scan command handlers."""

from __future__ import annotations

import asyncio
from typing import Annotated

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from navil.core.engine import NavilEngine
from navil.knowledge.models import ScanRequest


def register(app: typer.Typer) -> None:
    @app.command("scan")
    def scan_command(
        target: Annotated[list[str], typer.Argument(help="One or more target URLs")],
        scope: Annotated[str, typer.Option("--scope", help="Scope file path")] = ".navil-scope.yml",
        plugins: Annotated[str, typer.Option("--plugins", help="Comma-separated plugin names")] = "",
        max_depth: Annotated[int | None, typer.Option("--depth", min=1, max=10)] = None,
        wait: Annotated[bool, typer.Option("--wait/--no-wait", help="Wait for scan completion")] = True,
    ) -> None:
        plugin_names = [item.strip() for item in plugins.split(",") if item.strip()] or None

        async def _run() -> None:
            engine = NavilEngine()
            await engine.initialize()
            scan_id = await engine.start_scan(
                ScanRequest(
                    target_urls=target,
                    scope_path=scope,
                    plugin_names=plugin_names,
                    max_depth=max_depth,
                )
            )
            typer.echo(f"Scan started: {scan_id}")
            if not wait:
                return

            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Running scan...", total=None)
                while True:
                    result = await engine.get_scan(scan_id)
                    if result is None:
                        progress.update(task, description="Scan not found")
                        break
                    progress.update(task, description=f"Status: {result.status.value}")
                    if result.status.value in {"COMPLETED", "FAILED", "CANCELED"}:
                        break
                    await asyncio.sleep(1.0)

                final = await engine.get_scan(scan_id)
                if final:
                    typer.echo(f"Final status: {final.status.value}")
                    typer.echo(f"Findings: {len(final.findings)}")

        asyncio.run(_run())
