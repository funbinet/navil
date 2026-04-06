from __future__ import annotations

import os
import sys

from navil.cli.app import app as cli_app


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in {"cli", "--cli"}:
        sys.argv = [sys.argv[0], *sys.argv[2:]]
        cli_app()
        return

    if os.name != "nt" and not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        print("No GUI display detected. Falling back to CLI mode.")
        cli_app()
        return

    from navil.gui.app import main as gui_main

    gui_main()


if __name__ == "__main__":
    main()
