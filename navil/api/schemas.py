"""Pydantic schemas for API payloads."""

from __future__ import annotations

from pydantic import BaseModel, Field

from navil.knowledge.models import ScanStatus


class ScanCreateRequest(BaseModel):
    target_urls: list[str]
    scope_path: str = ".navil-scope.yml"
    plugin_names: list[str] | None = None
    max_depth: int | None = Field(default=None, ge=1, le=10)


class ScanCreateResponse(BaseModel):
    scan_id: str
    status: ScanStatus


class BrainTrainRequest(BaseModel):
    plugin_rewards: dict[str, float]
