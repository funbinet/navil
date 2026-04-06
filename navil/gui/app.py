"""GUI entrypoints."""

from __future__ import annotations

import sys
from typing import cast

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication

from navil.gui.main_window import NavilMainWindow
from navil.gui.theme import apply_theme


def run_gui() -> int:
    existing = QApplication.instance()
    if existing is None:
        app = QApplication(sys.argv)
    elif isinstance(existing, QApplication):
        app = existing
    else:
        app = cast(QApplication, QCoreApplication.instance())

    apply_theme(app)
    window = NavilMainWindow()
    window.show()
    return app.exec()


def main() -> None:
    raise SystemExit(run_gui())
