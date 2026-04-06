"""API middleware stack."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from navil.config import AppConfig


class TokenAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, config: AppConfig) -> None:
        super().__init__(app)
        self.config = config

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        path = request.url.path
        open_paths = {"/", "/health", "/docs", "/redoc", "/openapi.json"}
        if path.startswith("/dashboard") or path in open_paths or path.startswith("/ws/"):
            return await call_next(request)

        if path.startswith("/api"):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return JSONResponse(status_code=401, content={"detail": "Missing bearer token"})
            token = auth_header.removeprefix("Bearer ").strip()
            if token not in self.config.token_set:
                return JSONResponse(status_code=403, content={"detail": "Invalid API token"})

        return await call_next(request)


def install_middleware(app: FastAPI, config: AppConfig) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    app.add_middleware(TokenAuthMiddleware, config=config)
