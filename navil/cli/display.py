"""Rich display utilities for CLI output."""

from __future__ import annotations

from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from navil.knowledge.models import Finding

PANEL_WIDTH_CHARS = 68
console = Console(width=PANEL_WIDTH_CHARS)


def banner() -> None:
    logo = Text(
        "\n".join(
            [
                "▄▄  ▄▄  ▄▄▄  ▄▄ ▄▄ ▄▄ ▄▄",
                "███▄██ ██▀██ ██▄██ ██ ██",
                "██ ▀██ ██▀██  ▀█▀  ██ ██▄▄▄",
            ]
        ),
        style="bold bright_cyan",
        justify="center",
    )
    subtitle = Text(
        "Autonomous Scope-Enforced Security Assessment",
        style="bold spring_green3",
        justify="center",
    )
    content = Group(Align.center(logo), Align.center(subtitle))
    console.print(
        Panel(
            content,
            border_style="bright_green",
            width=PANEL_WIDTH_CHARS,
            expand=True,
        )
    )
    console.print()


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

    console.print(
        Panel(
            table,
            title="[bold cyan]Findings[/bold cyan]",
            border_style="grey54",
            width=PANEL_WIDTH_CHARS,
            expand=True,
        )
    )
