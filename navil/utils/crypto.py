"""Crypto and hashing utility helpers."""

from __future__ import annotations

import hashlib
import secrets


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def random_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)
