"""SQLite persistence for scans and findings."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import aiosqlite

from navil.knowledge.models import Finding, ScanResult, ScanStatus


class KnowledgeStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    async def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(
                """
                PRAGMA journal_mode = WAL;

                CREATE TABLE IF NOT EXISTS scans (
                    id TEXT PRIMARY KEY,
                    targets_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metrics_json TEXT NOT NULL,
                    errors_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS findings (
                    id TEXT PRIMARY KEY,
                    scan_id TEXT NOT NULL,
                    plugin TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    parameter_name TEXT,
                    payload TEXT,
                    evidence TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    chain_potential_json TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(scan_id) REFERENCES scans(id)
                );

                CREATE INDEX IF NOT EXISTS idx_findings_scan_id ON findings(scan_id);
                CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);
                """
            )
            await db.commit()

    async def upsert_scan(self, scan: ScanResult) -> None:
        now = datetime.now(UTC).isoformat()
        scan.updated_at = datetime.fromisoformat(now)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO scans (id, targets_json, status, metrics_json, errors_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    targets_json = excluded.targets_json,
                    status = excluded.status,
                    metrics_json = excluded.metrics_json,
                    errors_json = excluded.errors_json,
                    updated_at = excluded.updated_at
                """,
                (
                    scan.id,
                    json.dumps(scan.targets),
                    scan.status.value,
                    scan.metrics.model_dump_json(),
                    json.dumps(scan.errors),
                    scan.created_at.isoformat(),
                    now,
                ),
            )
            await db.commit()

    async def set_status(self, scan_id: str, status: ScanStatus, error: str | None = None) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT errors_json FROM scans WHERE id = ?", (scan_id,))
            row = await cursor.fetchone()
            errors: list[str] = []
            if row is not None and row[0]:
                errors = json.loads(row[0])
            if error:
                errors.append(error)

            await db.execute(
                "UPDATE scans SET status = ?, errors_json = ?, updated_at = ? WHERE id = ?",
                (status.value, json.dumps(errors), datetime.now(UTC).isoformat(), scan_id),
            )
            await db.commit()

    async def add_finding(self, finding: Finding) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO findings (
                    id, scan_id, plugin, severity, category, title, url, parameter_name,
                    payload, evidence, confidence, chain_potential_json, tags_json, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    finding.id,
                    finding.scan_id,
                    finding.plugin,
                    finding.severity.value,
                    finding.category,
                    finding.title,
                    finding.url,
                    finding.parameter,
                    finding.payload,
                    finding.evidence,
                    finding.confidence,
                    json.dumps(finding.chain_potential),
                    json.dumps(finding.tags),
                    finding.timestamp.isoformat(),
                ),
            )
            await db.commit()

    async def list_findings(self, scan_id: str | None = None) -> list[Finding]:
        query = "SELECT * FROM findings"
        params: tuple[str, ...] = ()
        if scan_id:
            query += " WHERE scan_id = ?"
            params = (scan_id,)

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()

        return [
            Finding(
                id=row["id"],
                scan_id=row["scan_id"],
                plugin=row["plugin"],
                severity=row["severity"],
                category=row["category"],
                title=row["title"],
                url=row["url"],
                parameter=row["parameter_name"],
                payload=row["payload"],
                evidence=row["evidence"],
                confidence=row["confidence"],
                chain_potential=json.loads(row["chain_potential_json"]),
                tags=json.loads(row["tags_json"]),
                timestamp=datetime.fromisoformat(row["timestamp"]),
            )
            for row in rows
        ]

    async def get_scan(self, scan_id: str) -> ScanResult | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
            row = await cursor.fetchone()
            if row is None:
                return None

        findings = await self.list_findings(scan_id)
        from navil.knowledge.models import ScanMetrics

        return ScanResult(
            id=row["id"],
            targets=json.loads(row["targets_json"]),
            status=ScanStatus(row["status"]),
            findings=findings,
            endpoints=[],
            metrics=ScanMetrics.model_validate_json(row["metrics_json"]),
            errors=json.loads(row["errors_json"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    async def list_scans(self, limit: int = 25) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, status, targets_json, metrics_json, errors_json, updated_at
                FROM scans
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = await cursor.fetchall()

        results: list[dict[str, Any]] = []
        for row in rows:
            metrics = json.loads(row["metrics_json"])
            results.append(
                {
                    "id": row["id"],
                    "status": row["status"],
                    "targets": json.loads(row["targets_json"]),
                    "metrics": metrics,
                    "errors": json.loads(row["errors_json"]),
                    "updated_at": row["updated_at"],
                }
            )
        return results
