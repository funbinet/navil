"""Async scope-aware crawler."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol
from urllib.parse import parse_qs, urlparse

import httpx

from navil.config import TargetScope
from navil.knowledge.models import DiscoveredEndpoint
from navil.recon.auth import TargetCredentials
from navil.recon.spider import extract_forms, extract_links
from navil.recon.tech_detect import detect_technologies
from navil.utils.http import build_async_client
from navil.utils.rate_limiter import AsyncRateLimiter


@dataclass(slots=True)
class CrawlReport:
    endpoints: list[DiscoveredEndpoint] = field(default_factory=list)
    technologies: dict[str, str] = field(default_factory=dict)
    request_count: int = 0


class ScopeContract(Protocol):
    def is_allowed(self, url: str, method: str = "GET") -> bool:
        ...


class ReconCrawler:
    def __init__(self) -> None:
        self.rate_limiter = AsyncRateLimiter()

    async def crawl(
        self,
        target: TargetScope,
        scope: ScopeContract,
        credentials: TargetCredentials | None = None,
    ) -> CrawlReport:
        report = CrawlReport()
        queue: list[tuple[str, int]] = [(str(target.base_url), 0)]
        visited: set[str] = set()

        async with build_async_client() as client:
            if credentials:
                client.auth = (credentials.username, credentials.password)

            while queue:
                url, depth = queue.pop(0)
                if url in visited or depth > target.max_depth:
                    continue
                if not scope.is_allowed(url, "GET"):
                    continue

                visited.add(url)
                parsed = urlparse(url)
                await self.rate_limiter.wait(parsed.netloc, target.rate_limit_rps)

                try:
                    response = await client.get(url)
                except httpx.HTTPError:
                    continue

                report.request_count += 1
                params = sorted(parse_qs(parsed.query).keys())
                report.endpoints.append(
                    DiscoveredEndpoint(
                        url=url,
                        method="GET",
                        source="crawler",
                        depth=depth,
                        params=params,
                        response_code=response.status_code,
                    )
                )

                if not report.technologies:
                    report.technologies = detect_technologies(dict(response.headers), response.text)

                for link in extract_links(url, response.text):
                    if link not in visited and scope.is_allowed(link, "GET"):
                        queue.append((link, depth + 1))

                for form in extract_forms(url, response.text):
                    if not scope.is_allowed(form.action, form.method):
                        continue
                    report.endpoints.append(
                        DiscoveredEndpoint(
                            url=form.action,
                            method=form.method,
                            source="form",
                            depth=depth,
                            params=form.fields,
                        )
                    )

        deduped: dict[tuple[str, str], DiscoveredEndpoint] = {}
        for endpoint in report.endpoints:
            deduped[(endpoint.url, endpoint.method)] = endpoint
        report.endpoints = list(deduped.values())
        return report
