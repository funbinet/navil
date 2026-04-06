"""CSRF token weakness detector."""

from __future__ import annotations

from navil.knowledge.models import Finding, Severity
from navil.scanner.base import ScanContext, VulnPlugin
from navil.scanner.plugins.common import build_finding

TOKEN_HINTS = {"csrf", "token", "xsrf", "authenticity_token"}


class CsrfPlugin(VulnPlugin):
    name = "csrf"
    severity = Severity.MEDIUM
    category = "Broken Access Control"

    async def scan(self, context: ScanContext) -> list[Finding]:
        if context.endpoint.method.upper() != "POST":
            return []

        field_names = {param.lower() for param in context.endpoint.params}
        if field_names & TOKEN_HINTS:
            return []

        return [
            build_finding(
                self,
                context,
                "Potential Missing CSRF Protection",
                "POST form/action discovered without obvious CSRF token parameter",
                confidence=0.6,
            )
        ]
