from __future__ import annotations

from pathlib import Path

import pytest

from navil.cli.local_audit import audit_path


def test_audit_path_detects_world_writable_file(tmp_path: Path) -> None:
    target = tmp_path / "open.txt"
    target.write_text("data", encoding="utf-8")
    target.chmod(0o666)

    result = audit_path(tmp_path, max_depth=3, max_entries=200)

    assert result.files_scanned >= 1
    assert any(item.category == "world-writable-file" for item in result.findings)


def test_audit_path_raises_for_missing_path(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        audit_path(missing)
