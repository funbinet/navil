"""Validation helpers used across scanner and API."""

from __future__ import annotations

from urllib.parse import urlparse


def is_safe_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def normalize_method(method: str) -> str:
    return method.strip().upper()


def matches_prefix(path: str, prefixes: list[str]) -> bool:
    if not prefixes:
        return True
    return any(path.startswith(prefix.rstrip("*")) for prefix in prefixes)
