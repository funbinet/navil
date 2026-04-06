"""Rich display utilities for CLI output."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from navil.knowledge.models import Finding

console = Console()


def banner() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]NAVIL[/bold cyan]\n[dim]Autonomous Scope-Enforced Security Assessment[/dim]",
            border_style="bright_green",
        )
    )


def print_findings(findings: list[Finding]) -> None:
    table = Table(title="Findings")
    table.add_column("Severity", style="bold")
    table.add_column("Plugin")
    table.add_column("URL")
    table.add_column("Title")
    table.add_column("Confidence")

    for finding in findings:
        table.add_row(
            finding.severity.value,
            finding.plugin,
            finding.url,
            finding.title,
            f"{finding.confidence:.2f}",
        )

    console.print(table)
