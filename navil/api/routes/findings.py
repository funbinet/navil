"""Findings query routes."""

from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Request

from navil.core.engine import NavilEngine

router = APIRouter(prefix="/api/findings", tags=["findings"])


def _engine(request: Request) -> NavilEngine:
    return cast(NavilEngine, request.app.state.engine)


@router.get("")
async def list_findings(request: Request, scan_id: str | None = None) -> dict[str, object]:
    engine = _engine(request)
    findings = await engine.list_findings(scan_id)
    return {"count": len(findings), "findings": [item.model_dump(mode="json") for item in findings]}
