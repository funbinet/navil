"""Information disclosure detector plugin."""

from __future__ import annotations

import re

from navil.knowledge.models import Finding, Severity
from navil.scanner.base import ScanContext, VulnPlugin
from navil.scanner.plugins.common import build_finding

PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private_key_marker": re.compile(r"-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----"),
}


class InfoDisclosurePlugin(VulnPlugin):
    name = "info_disclosure"
    severity = Severity.MEDIUM
    category = "Sensitive Data Exposure"

    async def scan(self, context: ScanContext) -> list[Finding]:
        if context.response is None:
            return []

        findings: list[Finding] = []
        body = context.response.text
        for label, pattern in PATTERNS.items():
            match = pattern.search(body)
            if not match:
                continue
            findings.append(
                build_finding(
                    self,
                    context,
                    f"Potential Information Disclosure: {label}",
                    f"Matched pattern '{label}' near: {match.group(0)[:80]}",
                    confidence=0.75,
                    tags=["sensitive-data", label],
                )
            )
        return findings
