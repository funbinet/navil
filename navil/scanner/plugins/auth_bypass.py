"""Authentication bypass heuristic plugin."""

from __future__ import annotations

from urllib.parse import urlparse

from navil.knowledge.models import Finding, Severity
from navil.scanner.base import ScanContext, VulnPlugin
from navil.scanner.plugins.common import build_finding

SENSITIVE_SEGMENTS = {"admin", "management", "internal", "backoffice", "root"}


class AuthBypassPlugin(VulnPlugin):
    name = "auth_bypass"
    severity = Severity.HIGH
    category = "Broken Authentication"

    async def scan(self, context: ScanContext) -> list[Finding]:
        if context.response is None:
            return []

        path = urlparse(context.endpoint.url).path.lower()
        if not any(segment in path for segment in SENSITIVE_SEGMENTS):
            return []

        if context.response.status_code in {200, 201, 204}:
            return [
                build_finding(
                    self,
                    context,
                    "Potential Authorization Bypass",
                    f"Sensitive path '{path}' responded with status {context.response.status_code}",
                    confidence=0.65,
                    chain_potential=["idor", "info_disclosure"],
                )
            ]
        return []
