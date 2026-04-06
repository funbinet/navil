"""Nuclei execution adapter."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def run_nuclei_templates(target: str, templates_path: Path | None = None) -> dict[str, object]:
    nuclei_path = shutil.which("nuclei")
    if nuclei_path is None:
        return {"available": False, "error": "nuclei binary not found"}

    cmd = [nuclei_path, "-u", target, "-silent"]
    if templates_path:
        cmd.extend(["-t", str(templates_path)])

    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
    return {
        "available": True,
        "returncode": completed.returncode,
        "stdout": completed.stdout.splitlines(),
        "stderr": completed.stderr.splitlines(),
    }
