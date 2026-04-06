"""Adaptive brain status and control routes."""

from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Request

from navil.api.schemas import BrainTrainRequest
from navil.core.engine import NavilEngine

router = APIRouter(prefix="/api/brain", tags=["brain"])


def _engine(request: Request) -> NavilEngine:
    return cast(NavilEngine, request.app.state.engine)


@router.get("/status")
async def brain_status(request: Request) -> dict[str, object]:
    return _engine(request).brain_status()


@router.post("/train")
async def brain_train(payload: BrainTrainRequest, request: Request) -> dict[str, object]:
    engine = _engine(request)
    engine.trainer.online_update(payload.plugin_rewards, source="api")
    engine.brain.save()
    return {"status": "ok", "updated_plugins": len(payload.plugin_rewards)}


@router.get("/metrics")
async def brain_metrics(request: Request) -> dict[str, object]:
    return _engine(request).brain_status()
