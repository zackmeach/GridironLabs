"""Thin QSettings wrapper for UI persistence.

Conventions (from recommendation.txt):
  ui/pages/<page_id>/tables/<table_id>/...
Version keys when structure changes.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QSettings


@dataclass(frozen=True)
class SettingsStore:
    """Namespaced accessors for UI persistence."""

    settings: QSettings
    base_prefix: str = "ui"

    def key(self, *parts: str) -> str:
        cleaned = [p.strip("/").strip() for p in parts if p and str(p).strip()]
        prefix = self.base_prefix.strip("/").strip()
        return "/".join([prefix, *cleaned]) if prefix else "/".join(cleaned)

    def value(self, *parts: str, default=None):
        return self.settings.value(self.key(*parts), defaultValue=default)

    def set_value(self, *parts: str, value) -> None:
        self.settings.setValue(self.key(*parts), value)


__all__ = ["SettingsStore"]

