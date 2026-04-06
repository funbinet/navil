"""Basic technology detection heuristics."""

from __future__ import annotations

import re

SIGNATURES = {
    "wordpress": re.compile(r"wp-content|wordpress", re.IGNORECASE),
    "react": re.compile(r"react|__next", re.IGNORECASE),
    "vue": re.compile(r"vue|nuxt", re.IGNORECASE),
    "angular": re.compile(r"ng-version|angular", re.IGNORECASE),
    "jquery": re.compile(r"jquery", re.IGNORECASE),
}


def detect_technologies(headers: dict[str, str], body: str) -> dict[str, str]:
    detected: dict[str, str] = {}
    server = headers.get("server")
    if server:
        detected["server"] = server
    powered = headers.get("x-powered-by")
    if powered:
        detected["powered_by"] = powered

    for name, pattern in SIGNATURES.items():
        if pattern.search(body):
            detected[name] = "detected"
    return detected
