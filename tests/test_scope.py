from __future__ import annotations

from pathlib import Path

from navil.config import load_scope
from navil.core.scope import ScopeEnforcer


def test_scope_enforcer_allows_expected_url(scope_file: Path) -> None:
    scope = load_scope(scope_file)
    enforcer = ScopeEnforcer(scope)
    assert enforcer.is_allowed("https://example.com/profile?id=1", "GET")
    assert not enforcer.is_allowed("https://evil.example.com", "GET")
    assert not enforcer.is_allowed("http://example.com", "GET")
