"""Plugin registry and loader."""

from __future__ import annotations

from navil.scanner.base import VulnPlugin
from navil.scanner.plugins import DEFAULT_PLUGINS


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, VulnPlugin] = {plugin.name: plugin for plugin in DEFAULT_PLUGINS}

    def all(self) -> list[VulnPlugin]:
        return list(self._plugins.values())

    def get(self, name: str) -> VulnPlugin:
        try:
            return self._plugins[name]
        except KeyError as exc:
            raise ValueError(f"Unknown plugin: {name}") from exc

    def select(self, names: list[str] | None) -> list[VulnPlugin]:
        if not names:
            return self.all()
        return [self.get(name) for name in names]
