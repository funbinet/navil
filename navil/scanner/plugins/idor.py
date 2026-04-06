"""IDOR heuristic detector plugin."""

from __future__ import annotations

from navil.knowledge.models import Finding, Severity
from navil.scanner.base import ScanContext, VulnPlugin
from navil.scanner.plugins.common import build_finding

ID_HINTS = {"id", "user_id", "account_id", "order_id", "profile_id", "uid"}


class IdorPlugin(VulnPlugin):
    name = "idor"
    severity = Severity.MEDIUM
    category = "Broken Access Control"

    async def scan(self, context: ScanContext) -> list[Finding]:
        for param in context.endpoint.params:
            if param.lower() in ID_HINTS:
                return [
                    build_finding(
                        self,
                        context,
                        "Potential IDOR Surface",
                        f"Endpoint exposes potentially sensitive identifier parameter: {param}",
                        parameter=param,
                        confidence=0.55,
                        chain_potential=["auth_bypass", "info_disclosure"],
                    )
                ]
        return []
