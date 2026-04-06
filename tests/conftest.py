from __future__ import annotations

from pathlib import Path

import pytest
import yaml


@pytest.fixture()
def scope_file(tmp_path: Path) -> Path:
    payload = {
        "version": 1,
        "project": "test-project",
        "authorization": {"mode": "direct", "note": "test"},
        "targets": [
            {
                "name": "test-target",
                "base_url": "https://example.com",
                "allowed_methods": ["GET", "POST"],
                "max_depth": 3,
                "rate_limit_rps": 5.0,
                "include_paths": ["/"],
                "exclude_paths": ["/admin/delete"],
            }
        ],
        "credentials": {
            "enabled": False,
            "username_env": "NAVIL_TARGET_USERNAME",
            "password_env": "NAVIL_TARGET_PASSWORD",
        },
        "safety": {
            "max_requests": 100,
            "stop_on_high_risk": False,
            "require_https": True,
            "allowed_ports": [443],
        },
    }
    path = tmp_path / "scope.yml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    return path
