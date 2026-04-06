"""Encoding and obfuscation helpers for payload mutation."""

from __future__ import annotations

import base64
import html
import random
import urllib.parse


def url_encode(payload: str) -> str:
    return urllib.parse.quote(payload, safe="")


def double_url_encode(payload: str) -> str:
    return urllib.parse.quote(url_encode(payload), safe="")


def html_entity_encode(payload: str) -> str:
    return "".join(f"&#{ord(char)};" for char in payload)


def base64_wrap(payload: str) -> str:
    encoded = base64.b64encode(payload.encode("utf-8")).decode("ascii")
    return f"base64:{encoded}"


def random_case(payload: str) -> str:
    chars = []
    for char in payload:
        if not char.isalpha():
            chars.append(char)
            continue
        chars.append(char.upper() if random.random() > 0.5 else char.lower())
    return "".join(chars)


def sql_comment_insert(payload: str) -> str:
    return payload.replace(" ", "/**/")


def stack(payload: str, strategies: list[str]) -> str:
    result = payload
    for strategy in strategies:
        if strategy == "url":
            result = url_encode(result)
        elif strategy == "double-url":
            result = double_url_encode(result)
        elif strategy == "html":
            result = html_entity_encode(result)
        elif strategy == "base64":
            result = base64_wrap(result)
        elif strategy == "case":
            result = random_case(result)
        elif strategy == "sql-comment":
            result = sql_comment_insert(result)
        elif strategy == "escape-html":
            result = html.escape(result)
    return result
