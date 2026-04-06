"""HTTP utility wrapper for consistent client behavior."""

from __future__ import annotations

import httpx

from navil.constants import DEFAULT_REQUEST_TIMEOUT_SECONDS


def build_async_client(*, verify: bool = True) -> httpx.AsyncClient:
    timeout = httpx.Timeout(DEFAULT_REQUEST_TIMEOUT_SECONDS)
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
    return httpx.AsyncClient(timeout=timeout, verify=verify, follow_redirects=True, limits=limits)
