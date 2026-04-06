"""Open redirect detector plugin."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from navil.knowledge.models import Finding, Severity
from navil.scanner.base import ScanContext, VulnPlugin
from navil.scanner.plugins.common import build_finding

REDIRECT_PARAMS = {"next", "url", "redirect", "return", "continue", "dest"}


class OpenRedirectPlugin(VulnPlugin):
    name = "open_redirect"
    severity = Severity.MEDIUM
    category = "Security Misconfiguration"

    async def scan(self, context: ScanContext) -> list[Finding]:
        parsed = urlparse(context.endpoint.url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        candidate_keys = [key for key in query if key.lower() in REDIRECT_PARAMS]
        if not candidate_keys:
            return []

        for key in candidate_keys:
            mutated = dict(query)
            mutated[key] = "https://example.org/navil-probe"
            candidate_url = urlunparse(parsed._replace(query=urlencode(mutated, doseq=True)))
            try:
                response = await context.client.get(candidate_url, follow_redirects=False)
            except Exception:
                continue

            location = response.headers.get("location", "")
            if location.startswith("https://example.org/"):
                return [
                    build_finding(
                        self,
                        context,
                        "Potential Open Redirect",
                        f"Redirect parameter '{key}' reflected into Location header: {location}",
                        parameter=key,
                        payload="https://example.org/navil-probe",
                        confidence=0.85,
                        chain_potential=["ssrf", "phishing"],
                    )
                ]
        return []
