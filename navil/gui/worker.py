"""Background scan worker for Qt GUI."""

from __future__ import annotations

import asyncio

from PyQt6.QtCore import QThread, pyqtSignal

from navil.core.engine import NavilEngine
from navil.knowledge.models import ScanRequest


class ScanWorker(QThread):
    progress = pyqtSignal(dict)
    completed = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, request: ScanRequest) -> None:
        super().__init__()
        self.request = request
        self._cancel_requested = False

    def request_cancel(self) -> None:
        self._cancel_requested = True

    def run(self) -> None:
        try:
            asyncio.run(self._run())
        except Exception as exc:  # pragma: no cover - Qt thread exception handling
            self.failed.emit(str(exc))

    async def _run(self) -> None:
        engine = NavilEngine()
        await engine.initialize()

        scan_id = await engine.start_scan(self.request)
        self.progress.emit({"type": "started", "scan_id": scan_id})

        while True:
            if self._cancel_requested:
                await engine.cancel_scan(scan_id)

            scan = await engine.get_scan(scan_id)
            if scan is None:
                await asyncio.sleep(0.7)
                continue

            payload = scan.model_dump(mode="json")
            self.progress.emit({"type": "update", "scan": payload})

            if scan.status.value in {"COMPLETED", "FAILED", "CANCELED"}:
                self.completed.emit(payload)
                return

            await asyncio.sleep(1.0)
