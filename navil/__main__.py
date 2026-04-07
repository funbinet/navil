from __future__ import annotations

import sys

from navil.cli.app import app as cli_app


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in {"cli", "--cli"}:
        sys.argv = [sys.argv[0], *sys.argv[2:]]
    cli_app()


if __name__ == "__main__":
    main()
