from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from navil.knowledge.models import Finding, ScanResult, ScanStatus, Severity
from navil.knowledge.store import KnowledgeStore


@pytest.mark.asyncio
async def test_store_persists_scan_and_finding(tmp_path: Path) -> None:
    store = KnowledgeStore(tmp_path / "navil.db")
    await store.initialize()

    scan = ScanResult(id="scan-1", targets=["https://example.com"], status=ScanStatus.RUNNING)
    await store.upsert_scan(scan)

    finding = Finding(
        id="f-1",
        scan_id="scan-1",
        plugin="headers",
        severity=Severity.LOW,
        category="misconfig",
        title="Missing Header",
        url="https://example.com",
        evidence="x-frame-options missing",
        timestamp=datetime.now(UTC),
    )
    await store.add_finding(finding)

    loaded = await store.get_scan("scan-1")
    assert loaded is not None
    findings = await store.list_findings("scan-1")
    assert len(findings) == 1
