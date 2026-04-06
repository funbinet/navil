"""Scan management routes."""

from __future__ import annotations

from typing import cast

from fastapi import APIRouter, HTTPException, Request

from navil.api.schemas import ScanCreateRequest, ScanCreateResponse
from navil.core.engine import NavilEngine
from navil.knowledge.models import ScanRequest, ScanStatus

router = APIRouter(prefix="/api/scans", tags=["scans"])


def _engine(request: Request) -> NavilEngine:
    return cast(NavilEngine, request.app.state.engine)


@router.post("", response_model=ScanCreateResponse)
async def create_scan(payload: ScanCreateRequest, request: Request) -> ScanCreateResponse:
    engine = _engine(request)
    scan_id = await engine.start_scan(
        ScanRequest(
            target_urls=payload.target_urls,
            scope_path=payload.scope_path,
            plugin_names=payload.plugin_names,
            max_depth=payload.max_depth,
        )
    )
    return ScanCreateResponse(scan_id=scan_id, status=ScanStatus.PENDING)


@router.get("/{scan_id}")
async def get_scan(scan_id: str, request: Request) -> dict[str, object]:
    engine = _engine(request)
    scan = await engine.get_scan(scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan.model_dump(mode="json")


@router.get("/{scan_id}/findings")
async def get_scan_findings(scan_id: str, request: Request) -> dict[str, object]:
    engine = _engine(request)
    findings = await engine.list_findings(scan_id)
    return {"scan_id": scan_id, "findings": [item.model_dump(mode="json") for item in findings]}


@router.delete("/{scan_id}")
async def cancel_scan(scan_id: str, request: Request) -> dict[str, object]:
    engine = _engine(request)
    canceled = await engine.cancel_scan(scan_id)
    if not canceled:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {"scan_id": scan_id, "status": "canceled"}
