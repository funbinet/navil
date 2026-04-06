"""Burp-compatible issue export."""

from __future__ import annotations

import json
from pathlib import Path

from navil.knowledge.models import Finding


def export_burp_issue_json(findings: list[Finding], output: Path) -> Path:
    payload = {
        "issues": [
            {
                "name": finding.title,
                "severity": finding.severity.value,
                "confidence": finding.confidence,
                "host": finding.url,
                "detail": finding.evidence,
                "type": finding.plugin,
            }
            for finding in findings
        ]
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output
