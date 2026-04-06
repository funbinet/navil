"""Route exports."""

from navil.api.routes.brain import router as brain_router
from navil.api.routes.config import router as config_router
from navil.api.routes.findings import router as findings_router
from navil.api.routes.scans import router as scans_router
from navil.api.routes.ws import router as ws_router

__all__ = [
    "brain_router",
    "config_router",
    "findings_router",
    "scans_router",
    "ws_router",
]
