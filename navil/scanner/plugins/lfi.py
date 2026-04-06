"""Local file inclusion surface detector."""

from __future__ import annotations

from navil.knowledge.models import Finding, Severity
from navil.scanner.base import ScanContext, VulnPlugin
from navil.scanner.plugins.common import build_finding

LFI_PARAMS = {"file", "path", "template", "page", "include", "document"}


class LfiPlugin(VulnPlugin):
    name = "lfi"
    severity = Severity.HIGH
    category = "Path Traversal"

    async def scan(self, context: ScanContext) -> list[Finding]:
        for param in context.endpoint.params:
            if param.lower() in LFI_PARAMS:
                return [
                    build_finding(
                        self,
                        context,
                        "Potential File Inclusion Surface",
                        f"Parameter '{param}' appears file-system related",
                        parameter=param,
                        confidence=0.62,
                        chain_potential=["rce", "info_disclosure"],
                    )
                ]
        return []
