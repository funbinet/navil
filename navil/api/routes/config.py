"""Configuration and scope helper routes."""

from __future__ import annotations

from fastapi import APIRouter

from navil.config import dump_scope, load_scope

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/scope/validate")
async def validate_scope(path: str = ".navil-scope.yml") -> dict[str, object]:
    scope = load_scope(path)
    return {"valid": True, "scope": dump_scope(scope)}
