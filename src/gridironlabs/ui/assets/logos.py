"""Team logo loading + caching.

Logos are treated as external assets located at:
  <GRIDIRONLABS_ROOT>/data/external/logos/<ABBR>.png

This module centralizes resolution and caches scaled pixmaps by (abbr, size).
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from gridironlabs.core.config import AppPaths

_pixmap_cache: dict[tuple[str, int], QPixmap] = {}


def _logos_dir() -> Path:
    paths = AppPaths.from_env()
    return paths.data_external / "logos"


def get_logo_pixmap(team_abbr: str, *, size: int) -> QPixmap | None:
    """Return a cached, scaled pixmap for a team abbreviation (e.g. 'PIT')."""
    abbr = team_abbr.strip().upper()
    if not abbr:
        return None

    key = (abbr, int(size))
    if key in _pixmap_cache:
        return _pixmap_cache[key]

    path = _logos_dir() / f"{abbr}.png"
    if not path.exists():
        return None

    pixmap = QPixmap(str(path))
    if pixmap.isNull():
        return None

    scaled = pixmap.scaled(int(size), int(size), Qt.KeepAspectRatio, Qt.SmoothTransformation)
    _pixmap_cache[key] = scaled
    return scaled


