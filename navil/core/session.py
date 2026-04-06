"""In-memory scan session and event tracking."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import UTC, datetime

from navil.knowledge.models import DiscoveredEndpoint, Finding, ScanEvent, ScanResult, ScanStatus


class SessionManager:
    def __init__(self) -> None:
        self._scans: dict[str, ScanResult] = {}
        self._subscribers: dict[str, list[asyncio.Queue[ScanEvent]]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def create(self, scan: ScanResult) -> None:
        async with self._lock:
            self._scans[scan.id] = scan

    async def get(self, scan_id: str) -> ScanResult | None:
        async with self._lock:
            return self._scans.get(scan_id)

    async def all(self) -> list[ScanResult]:
        async with self._lock:
            return list(self._scans.values())

    async def set_status(self, scan_id: str, status: ScanStatus) -> None:
        async with self._lock:
            scan = self._scans.get(scan_id)
            if scan is None:
                return
            scan.status = status
            scan.updated_at = datetime.now(UTC)

    async def add_endpoints(self, scan_id: str, endpoints: list[DiscoveredEndpoint]) -> None:
        async with self._lock:
            scan = self._scans.get(scan_id)
            if scan is None:
                return
            scan.endpoints.extend(endpoints)
            scan.metrics.discovered_endpoints = len(scan.endpoints)
            scan.updated_at = datetime.now(UTC)

    async def add_findings(self, scan_id: str, findings: list[Finding]) -> None:
        async with self._lock:
            scan = self._scans.get(scan_id)
            if scan is None:
                return
            scan.findings.extend(findings)
            scan.metrics.findings_total = len(scan.findings)
            distribution: dict[str, int] = {}
            for finding in scan.findings:
                key = finding.severity.value
                distribution[key] = distribution.get(key, 0) + 1
            scan.metrics.findings_by_severity = distribution
            scan.updated_at = datetime.now(UTC)

    async def add_error(self, scan_id: str, error: str) -> None:
        async with self._lock:
            scan = self._scans.get(scan_id)
            if scan is None:
                return
            scan.errors.append(error)
            scan.updated_at = datetime.now(UTC)

    async def subscribe(self, scan_id: str) -> asyncio.Queue[ScanEvent]:
        queue: asyncio.Queue[ScanEvent] = asyncio.Queue(maxsize=100)
        async with self._lock:
            self._subscribers[scan_id].append(queue)
        return queue

    async def publish(self, scan_id: str, event_type: str, message: str, payload: dict[str, object] | None = None) -> None:
        event = ScanEvent(type=event_type, scan_id=scan_id, message=message, payload=payload or {})
        async with self._lock:
            subscribers = list(self._subscribers.get(scan_id, []))
        for queue in subscribers:
            if queue.full():
                continue
            await queue.put(event)
