"""Active scanner orchestration for endpoint/plugin execution."""

from __future__ import annotations

import asyncio

from navil.knowledge.models import DiscoveredEndpoint, Finding
from navil.scanner.base import ScanContext, VulnPlugin
from navil.utils.http import build_async_client


class ActiveScanner:
    def __init__(self, plugins: list[VulnPlugin], concurrency: int = 20) -> None:
        self.plugins = plugins
        self._semaphore = asyncio.Semaphore(concurrency)

    async def scan_endpoints(self, scan_id: str, endpoints: list[DiscoveredEndpoint]) -> list[Finding]:
        findings: list[Finding] = []

        async with build_async_client() as client:
            async def scan_endpoint(endpoint: DiscoveredEndpoint) -> list[Finding]:
                async with self._semaphore:
                    method = endpoint.method
                    url = endpoint.url
                    try:
                        response = await client.request(method, url)
                    except Exception:
                        response = None

                    ctx = ScanContext(
                        scan_id=scan_id,
                        endpoint=endpoint,
                        client=client,
                        response=response,
                    )

                    endpoint_findings: list[Finding] = []
                    for plugin in self.plugins:
                        try:
                            endpoint_findings.extend(await plugin.scan(ctx))
                        except Exception:
                            continue
                    return endpoint_findings

            grouped = await asyncio.gather(*(scan_endpoint(endpoint) for endpoint in endpoints))

        for endpoint_findings in grouped:
            findings.extend(endpoint_findings)
        return findings
