"""Reflected XSS heuristic detector."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from navil.knowledge.models import Finding, Severity
from navil.scanner.base import ScanContext, VulnPlugin
from navil.scanner.plugins.common import build_finding


class XssPlugin(VulnPlugin):
    name = "xss"
    severity = Severity.HIGH
    category = "Injection"

    def get_payloads(self) -> list[str]:
        return ["navil_xss_probe_123"]

    async def scan(self, context: ScanContext) -> list[Finding]:
        if not context.endpoint.params:
            return []

        parsed = urlparse(context.endpoint.url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))

        for payload in self.get_payloads():
            for param in context.endpoint.params:
                mutated = dict(query)
                mutated[param] = payload
                candidate_url = urlunparse(parsed._replace(query=urlencode(mutated, doseq=True)))
                try:
                    response = await context.client.get(candidate_url)
                except Exception:
                    continue

                if self.verify(response, payload):
                    return [
                        build_finding(
                            self,
                            context,
                            "Potential Reflected XSS",
                            f"Probe string reflected in response for parameter '{param}'",
                            parameter=param,
                            payload=payload,
                            confidence=0.7,
                            chain_potential=["auth_bypass", "session_hijack"],
                        )
                    ]
        return []
