"""Command injection surface detector plugin."""

from __future__ import annotations

from navil.knowledge.models import Finding, Severity
from navil.scanner.base import ScanContext, VulnPlugin
from navil.scanner.plugins.common import build_finding

RCE_PARAMS = {"cmd", "command", "exec", "execute", "shell", "daemon"}


class RcePlugin(VulnPlugin):
    name = "rce"
    severity = Severity.CRITICAL
    category = "Command Injection"

    async def scan(self, context: ScanContext) -> list[Finding]:
        for param in context.endpoint.params:
            if param.lower() in RCE_PARAMS:
                return [
                    build_finding(
                        self,
                        context,
                        "Potential Command Injection Surface",
                        f"Parameter '{param}' suggests command execution risk",
                        parameter=param,
                        confidence=0.55,
                        chain_potential=["privilege_escalation"],
                    )
                ]
        return []
