"""Core domain models for scanning and findings."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Severity(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ScanStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class DiscoveredEndpoint(BaseModel):
    url: str
    method: str = "GET"
    source: str = "crawl"
    depth: int = 0
    params: list[str] = Field(default_factory=list)
    response_code: int | None = None


class Finding(BaseModel):
    id: str
    scan_id: str
    plugin: str
    severity: Severity
    category: str
    title: str
    url: str
    parameter: str | None = None
    payload: str | None = None
    evidence: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    chain_potential: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def identity_key(self) -> str:
        return f"{self.plugin}:{self.url}:{self.parameter or '-'}:{self.title}"


class ScanMetrics(BaseModel):
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    requests_made: int = 0
    discovered_endpoints: int = 0
    findings_total: int = 0
    findings_by_severity: dict[str, int] = Field(default_factory=dict)
    reward_score: float = 0.0


class ScanResult(BaseModel):
    id: str
    targets: list[str]
    status: ScanStatus = ScanStatus.PENDING
    findings: list[Finding] = Field(default_factory=list)
    endpoints: list[DiscoveredEndpoint] = Field(default_factory=list)
    metrics: ScanMetrics = Field(default_factory=ScanMetrics)
    errors: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ScanRequest(BaseModel):
    target_urls: list[str]
    scope_path: str
    plugin_names: list[str] | None = None
    max_depth: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScanEvent(BaseModel):
    type: str
    scan_id: str
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
