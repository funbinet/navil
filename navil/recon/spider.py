"""Link and form extraction utilities."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


@dataclass(slots=True)
class FormEndpoint:
    action: str
    method: str
    fields: list[str]


def extract_links(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: set[str] = set()
    for anchor in soup.select("a[href]"):
        href = str(anchor.get("href") or "").strip()
        if not href or href.startswith(("javascript:", "mailto:", "tel:")):
            continue
        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            links.add(absolute)
    return sorted(links)


def extract_forms(base_url: str, html: str) -> list[FormEndpoint]:
    soup = BeautifulSoup(html, "html.parser")
    forms: list[FormEndpoint] = []
    for form in soup.select("form"):
        action = str(form.get("action") or "")
        method = str(form.get("method", "GET")).upper()
        fields: list[str] = []
        for field in form.select("input[name], textarea[name], select[name]"):
            name = field.get("name")
            if isinstance(name, str) and name:
                fields.append(name)
        forms.append(FormEndpoint(action=urljoin(base_url, action), method=method, fields=fields))
    return forms
