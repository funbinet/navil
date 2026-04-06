from __future__ import annotations

import httpx
import pytest

from navil.knowledge.models import DiscoveredEndpoint
from navil.scanner.base import ScanContext
from navil.scanner.plugins.sqli import SqliPlugin
from navil.scanner.plugins.xss import XssPlugin


class DummyClient:
    async def get(self, url: str | httpx.URL, **kwargs: object) -> httpx.Response:
        _ = kwargs
        raw_url = str(url)
        if "navil_xss_probe_123" in raw_url:
            return httpx.Response(200, text="navil_xss_probe_123")
        if "%27" in raw_url or "'" in raw_url:
            return httpx.Response(500, text="SQLite error near '")
        return httpx.Response(200, text="ok")

    async def request(
        self,
        method: str,
        url: str | httpx.URL,
        **kwargs: object,
    ) -> httpx.Response:
        _ = method, kwargs
        return await self.get(url)


@pytest.mark.asyncio
async def test_xss_plugin_detects_reflection() -> None:
    plugin = XssPlugin()
    ctx = ScanContext(
        scan_id="s1",
        endpoint=DiscoveredEndpoint(url="https://example.com?q=1", params=["q"]),
        client=DummyClient(),
        response=httpx.Response(200, text="ok"),
    )
    findings = await plugin.scan(ctx)
    assert findings
    assert findings[0].plugin == "xss"


@pytest.mark.asyncio
async def test_sqli_plugin_detects_error_pattern() -> None:
    plugin = SqliPlugin()
    ctx = ScanContext(
        scan_id="s1",
        endpoint=DiscoveredEndpoint(url="https://example.com?id=1", params=["id"]),
        client=DummyClient(),
        response=httpx.Response(200, text="ok"),
    )
    findings = await plugin.scan(ctx)
    assert findings
    assert findings[0].plugin == "sqli"
