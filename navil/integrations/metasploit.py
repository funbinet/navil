"""Metasploit verification adapter (non-interactive)."""

from __future__ import annotations

import shutil
import subprocess


def verify_with_metasploit(module: str, rhost: str, rport: int) -> dict[str, object]:
    msfconsole_path = shutil.which("msfconsole")
    if msfconsole_path is None:
        return {"available": False, "error": "msfconsole not found"}

    command = f"use {module}; set RHOSTS {rhost}; set RPORT {rport}; check; exit"
    completed = subprocess.run(
        [msfconsole_path, "-q", "-x", command],
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "available": True,
        "returncode": completed.returncode,
        "stdout": completed.stdout[-5000:],
        "stderr": completed.stderr[-5000:],
    }
