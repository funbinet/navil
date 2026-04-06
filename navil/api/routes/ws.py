"""WebSocket routes for real-time scan updates."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from navil.core.engine import NavilEngine

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/scan/{scan_id}")
async def scan_events(websocket: WebSocket, scan_id: str) -> None:
    await websocket.accept()
    engine: NavilEngine = websocket.app.state.engine
    queue = await engine.subscribe(scan_id)
    try:
        while True:
            event = await asyncio.wait_for(queue.get(), timeout=30)
            await websocket.send_json(event.model_dump(mode="json"))
    except TimeoutError:
        await websocket.send_json({"type": "keepalive", "scan_id": scan_id})
    except WebSocketDisconnect:
        return
