"""Sitemap and robots.txt discovery helpers."""

from __future__ import annotations

from urllib.parse import urljoin

import httpx


def candidate_discovery_urls(base_url: str) -> list[str]:
    return [
        urljoin(base_url, "/robots.txt"),
        urljoin(base_url, "/sitemap.xml"),
        urljoin(base_url, "/sitemap_index.xml"),
    ]


async def fetch_discovery_artifacts(client: httpx.AsyncClient, base_url: str) -> dict[str, str]:
    artifacts: dict[str, str] = {}
    for url in candidate_discovery_urls(base_url):
        try:
            response = await client.get(url)
            if response.status_code < 400 and response.text:
                artifacts[url] = response.text[:5000]
        except httpx.HTTPError:
            continue
    return artifacts
