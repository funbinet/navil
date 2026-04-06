"""Base plugin interfaces for vulnerability detection."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import httpx

from navil.knowledge.models import DiscoveredEndpoint, Finding, Severity


@dataclass(slots=True)
class ScanContext:
    scan_id: str
    endpoint: DiscoveredEndpoint
    client: Any
    response: httpx.Response | None
    metadata: dict[str, Any] = field(default_factory=dict)


class VulnPlugin(ABC):
    name: str
    severity: Severity
    category: str

    @abstractmethod
    async def scan(self, context: ScanContext) -> list[Finding]:
        """Inspect endpoint context and return validated findings."""

    def get_payloads(self) -> list[str]:
        return []

    def verify(self, response: httpx.Response, payload: str) -> bool:
        return payload in response.text
