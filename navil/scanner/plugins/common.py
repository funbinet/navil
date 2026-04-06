"""Shared helpers for plugin implementations."""

from __future__ import annotations

from uuid import uuid4

from navil.knowledge.models import Finding, Severity
from navil.scanner.base import ScanContext, VulnPlugin


def build_finding(
    plugin: VulnPlugin,
    context: ScanContext,
    title: str,
    evidence: str,
    *,
    parameter: str | None = None,
    payload: str | None = None,
    confidence: float = 0.6,
    chain_potential: list[str] | None = None,
    tags: list[str] | None = None,
    severity: Severity | None = None,
) -> Finding:
    return Finding(
        id=str(uuid4()),
        scan_id=context.scan_id,
        plugin=plugin.name,
        severity=severity or plugin.severity,
        category=plugin.category,
        title=title,
        url=context.endpoint.url,
        parameter=parameter,
        payload=payload,
        evidence=evidence,
        confidence=confidence,
        chain_potential=chain_potential or [],
        tags=tags or [],
    )
