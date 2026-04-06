"""Scope enforcement for authorized scanning."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from navil.config import ScopeFile, TargetScope
from navil.utils.validators import matches_prefix, normalize_method


class ScopeViolation(Exception):
    """Raised when a request is out of authorized scope."""


@dataclass(slots=True)
class ScopeEnforcer:
    scope: ScopeFile

    def target_for_url(self, url: str) -> TargetScope | None:
        candidate = urlparse(url)
        for target in self.scope.targets:
            base = urlparse(str(target.base_url))
            if candidate.netloc != base.netloc:
                continue
            if self.scope.safety.require_https and candidate.scheme != "https":
                continue
            if candidate.port and candidate.port not in self.scope.safety.allowed_ports:
                continue
            if target.include_paths and not matches_prefix(candidate.path or "/", target.include_paths):
                continue
            if target.exclude_paths and matches_prefix(candidate.path or "/", target.exclude_paths):
                continue
            return target
        return None

    def is_allowed(self, url: str, method: str = "GET") -> bool:
        target = self.target_for_url(url)
        if target is None:
            return False
        return normalize_method(method) in {normalize_method(item) for item in target.allowed_methods}

    def assert_allowed(self, url: str, method: str = "GET") -> TargetScope:
        target = self.target_for_url(url)
        if target is None:
            raise ScopeViolation(f"Out-of-scope URL: {url}")

        normalized_method = normalize_method(method)
        allowed = {normalize_method(item) for item in target.allowed_methods}
        if normalized_method not in allowed:
            raise ScopeViolation(f"Method {normalized_method} not allowed for {url}")

        return target

    def rate_limit_for(self, url: str) -> float:
        target = self.assert_allowed(url)
        return target.rate_limit_rps

    def max_depth_for(self, url: str) -> int:
        target = self.assert_allowed(url)
        return target.max_depth
