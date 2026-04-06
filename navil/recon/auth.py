"""Authentication helper for target sessions."""

from __future__ import annotations

import os
from dataclasses import dataclass

from navil.config import CredentialsConfig


@dataclass(slots=True)
class TargetCredentials:
    username: str
    password: str


def load_target_credentials(config: CredentialsConfig) -> TargetCredentials | None:
    if not config.enabled:
        return None
    username = os.getenv(config.username_env, "")
    password = os.getenv(config.password_env, "")
    if not username or not password:
        return None
    return TargetCredentials(username=username, password=password)
