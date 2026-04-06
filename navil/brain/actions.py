"""Action space definition for scan strategy selection."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ActionChoice:
    plugin_name: str
    payload_strategy: str = "default"
    encoding: str = "plain"
    rate_scale: float = 1.0
    chain_previous_finding: bool = False
