"""SQL injection heuristic detector."""

from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from navil.knowledge.models import Finding, Severity
from navil.scanner.base import ScanContext, VulnPlugin
from navil.scanner.plugins.common import build_finding

SQL_ERRORS = re.compile(
    r"(sql syntax|mysql|postgresql|sqlite error|odbc|unterminated string|sqlstate)",
    re.IGNORECASE,
)


class SqliPlugin(VulnPlugin):
    name = "sqli"
    severity = Severity.HIGH
    category = "Injection"

    def get_payloads(self) -> list[str]:
        return ["'", "\"", "' OR '1'='1"]

    async def scan(self, context: ScanContext) -> list[Finding]:
        if not context.endpoint.params:
            return []

        parsed = urlparse(context.endpoint.url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))

        for param in context.endpoint.params:
            for payload in self.get_payloads():
                mutated = dict(query)
                mutated[param] = payload
                candidate_url = urlunparse(parsed._replace(query=urlencode(mutated, doseq=True)))
                try:
                    response = await context.client.get(candidate_url)
                except Exception:
                    continue
                if SQL_ERRORS.search(response.text):
                    return [
                        build_finding(
                            self,
                            context,
                            "Potential SQL Injection Signal",
                            f"Database error signature detected for parameter '{param}'",
                            parameter=param,
                            payload=payload,
                            confidence=0.82,
                            chain_potential=["idor", "info_disclosure"],
                        )
                    ]
        return []
