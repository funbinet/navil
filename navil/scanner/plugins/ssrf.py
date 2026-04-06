"""SSRF surface detector plugin."""

from __future__ import annotations

from navil.knowledge.models import Finding, Severity
from navil.scanner.base import ScanContext, VulnPlugin
from navil.scanner.plugins.common import build_finding

SSRF_PARAMS = {"url", "uri", "target", "callback", "dest", "redirect", "next"}


class SsrfPlugin(VulnPlugin):
    name = "ssrf"
    severity = Severity.HIGH
    category = "Server Side Request Forgery"

    async def scan(self, context: ScanContext) -> list[Finding]:
        for param in context.endpoint.params:
            if param.lower() not in SSRF_PARAMS:
                continue
            return [
                build_finding(
                    self,
                    context,
                    "Potential SSRF Attack Surface",
                    f"URL-like parameter '{param}' may allow server-side outbound requests",
                    parameter=param,
                    confidence=0.58,
                    chain_potential=["open_redirect", "internal_pivot"],
                )
            ]
        return []
