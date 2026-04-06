"""Payload corpus management."""

from __future__ import annotations

import json
from pathlib import Path

from navil.constants import PAYLOAD_DIR


class PayloadCorpus:
    def __init__(self, payload_dir: Path | None = None) -> None:
        self.payload_dir = payload_dir or PAYLOAD_DIR

    def load(self, category: str) -> list[str]:
        path = self.payload_dir / f"{category}.json"
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [str(item) for item in payload]

    def save(self, category: str, payloads: list[str]) -> None:
        self.payload_dir.mkdir(parents=True, exist_ok=True)
        path = self.payload_dir / f"{category}.json"
        unique = sorted(set(payloads))
        path.write_text(json.dumps(unique, indent=2), encoding="utf-8")
