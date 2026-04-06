"""Security headers analysis plugin."""

from __future__ import annotations

from navil.constants import SECURITY_HEADERS
from navil.knowledge.models import Finding, Severity
from navil.scanner.base import ScanContext, VulnPlugin
from navil.scanner.plugins.common import build_finding


class HeadersPlugin(VulnPlugin):
    name = "headers"
    severity = Severity.LOW
    category = "Security Misconfiguration"

    async def scan(self, context: ScanContext) -> list[Finding]:
        if context.response is None:
            return []
        present = {key.lower() for key in context.response.headers.keys()}
        missing = sorted(SECURITY_HEADERS - present)
        if not missing:
            return []

        evidence = f"Missing security headers: {', '.join(missing)}"
        return [
            build_finding(
                self,
                context,
                "Missing Security Headers",
                evidence,
                confidence=0.9,
            )
        ]
