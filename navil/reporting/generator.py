"""Report generation orchestrator."""

from __future__ import annotations

from pathlib import Path

from navil.constants import REPORTS_DIR
from navil.knowledge.models import ScanResult
from navil.reporting.exporters import (
    template_environment,
    write_html,
    write_json,
    write_markdown,
    write_pdf,
)


class ReportGenerator:
    def __init__(self) -> None:
        self.template_dir = Path(__file__).resolve().parent / "templates"
        self.env = template_environment(self.template_dir)

    async def generate(self, scan: ScanResult, *, fmt: str = "html", output_path: Path | None = None) -> Path:
        fmt = fmt.lower()
        base = output_path or (REPORTS_DIR / f"{scan.id}.{fmt}")

        payload = scan.model_dump(mode="json")

        if fmt == "json":
            return write_json(base, payload)

        if fmt == "md":
            lines = [
                f"# Navil Report: {scan.id}",
                f"Status: {scan.status.value}",
                f"Targets: {', '.join(scan.targets)}",
                f"Findings: {len(scan.findings)}",
                "",
                "## Findings",
            ]
            for finding in scan.findings:
                lines.append(f"- [{finding.severity.value}] {finding.title} ({finding.url})")
            return write_markdown(base, "\n".join(lines))

        template = self.env.get_template("html_report.html")
        html = template.render(scan=scan)

        if fmt == "html":
            return write_html(base, html)

        if fmt == "pdf":
            return write_pdf(base, html)

        raise ValueError(f"Unsupported report format: {fmt}")
