"""FastAPI server bootstrapping."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from navil.api.middleware import install_middleware
from navil.api.routes import brain_router, config_router, findings_router, scans_router, ws_router
from navil.config import AppConfig
from navil.core.engine import NavilEngine
from navil.utils.logger import configure_logging

config = AppConfig()
configure_logging("INFO")
engine = NavilEngine(config)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await engine.initialize()
    yield


app = FastAPI(title="Navil API", version="0.1.0", lifespan=lifespan)
app.state.engine = engine
install_middleware(app, config)

app.include_router(scans_router)
app.include_router(findings_router)
app.include_router(brain_router)
app.include_router(config_router)
app.include_router(ws_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def index() -> dict[str, str]:
    return {
        "service": "navil-api",
        "health": "/health",
        "cli": "run with `python3 -m navil --help` or `navil --help`",
    }


def run() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080)
