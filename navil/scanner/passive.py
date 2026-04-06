"""Passive scanning profile."""

from __future__ import annotations

from navil.scanner.base import VulnPlugin

PASSIVE_PLUGIN_NAMES = {"headers", "cors", "info_disclosure"}


def passive_filter(plugins: list[VulnPlugin]) -> list[VulnPlugin]:
    return [plugin for plugin in plugins if plugin.name in PASSIVE_PLUGIN_NAMES]
