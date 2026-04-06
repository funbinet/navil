"""Simple pattern mining from findings data."""

from __future__ import annotations

from collections import Counter

from navil.knowledge.models import Finding


def summarize_finding_patterns(findings: list[Finding]) -> dict[str, object]:
    plugin_counts = Counter(finding.plugin for finding in findings)
    severity_counts = Counter(finding.severity.value for finding in findings)
    parameter_counts = Counter(finding.parameter for finding in findings if finding.parameter)

    return {
        "top_plugins": plugin_counts.most_common(5),
        "severity_distribution": dict(severity_counts),
        "common_parameters": parameter_counts.most_common(5),
        "total": len(findings),
    }
