"""Configuration and scope loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, HttpUrl, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from navil.constants import (
    DB_PATH,
    DEFAULT_MAX_DEPTH,
    DEFAULT_MAX_REQUESTS,
    DEFAULT_RATE_LIMIT_RPS,
    DEFAULT_SCAN_CONCURRENCY,
)


class TargetScope(BaseModel):
    name: str
    base_url: HttpUrl
    allowed_methods: list[str] = Field(default_factory=lambda: ["GET"])
    max_depth: int = Field(default=DEFAULT_MAX_DEPTH, ge=1, le=10)
    rate_limit_rps: float = Field(default=DEFAULT_RATE_LIMIT_RPS, gt=0.1, le=50.0)
    include_paths: list[str] = Field(default_factory=lambda: ["/"])
    exclude_paths: list[str] = Field(default_factory=list)


class CredentialsConfig(BaseModel):
    enabled: bool = False
    username_env: str = "NAVIL_TARGET_USERNAME"
    password_env: str = "NAVIL_TARGET_PASSWORD"


class SafetyConfig(BaseModel):
    max_requests: int = Field(default=DEFAULT_MAX_REQUESTS, ge=100, le=2_000_000)
    stop_on_high_risk: bool = False
    require_https: bool = True
    allowed_ports: list[int] = Field(default_factory=lambda: [443])


class AuthorizationConfig(BaseModel):
    mode: str = "direct"
    note: str = "Authorized testing only"


class ScopeFile(BaseModel):
    version: int = 1
    project: str = "navil-assessment"
    authorization: AuthorizationConfig = Field(default_factory=AuthorizationConfig)
    targets: list[TargetScope]
    credentials: CredentialsConfig = Field(default_factory=CredentialsConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NAVIL_", extra="ignore")

    environment: str = "development"
    db_path: Path = DB_PATH
    scan_concurrency: int = Field(default=DEFAULT_SCAN_CONCURRENCY, ge=1, le=1000)
    jwt_secret: str = "change-me-in-production"
    api_tokens: str = "local-dev-token"

    @property
    def token_set(self) -> set[str]:
        return {item.strip() for item in self.api_tokens.split(",") if item.strip()}


def load_scope(path: str | Path) -> ScopeFile:
    """Load and validate a Navil scope file."""
    scope_path = Path(path)
    if not scope_path.exists():
        raise FileNotFoundError(f"Scope file not found: {scope_path}")

    raw = yaml.safe_load(scope_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Scope file content must be a YAML object")

    try:
        return ScopeFile.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Invalid scope file: {exc}") from exc


def dump_scope(scope: ScopeFile) -> dict[str, Any]:
    """Return a serializable representation for APIs and docs."""
    return scope.model_dump(mode="json")
