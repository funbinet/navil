"""CORS misconfiguration detector."""

from __future__ import annotations

from navil.knowledge.models import Finding, Severity
from navil.scanner.base import ScanContext, VulnPlugin
from navil.scanner.plugins.common import build_finding


class CorsPlugin(VulnPlugin):
    name = "cors"
    severity = Severity.MEDIUM
    category = "Security Misconfiguration"

    async def scan(self, context: ScanContext) -> list[Finding]:
        probe_origin = "https://origin-probe.invalid"
        try:
            response = await context.client.get(context.endpoint.url, headers={"Origin": probe_origin})
        except Exception:
            return []

        acao = response.headers.get("access-control-allow-origin", "")
        acac = response.headers.get("access-control-allow-credentials", "").lower()
        if acao in {"*", probe_origin}:
            severity = Severity.HIGH if acao == "*" and acac == "true" else self.severity
            return [
                build_finding(
                    self,
                    context,
                    "Potentially Unsafe CORS Policy",
                    f"ACAO={acao!r} ACAC={acac!r}",
                    confidence=0.8,
                    severity=severity,
                )
            ]
        return []
