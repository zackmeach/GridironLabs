"""Settings page scaffold.

Settings is currently a minimal page that owns a `BasePage` grid canvas. Real
settings panels can be added incrementally.
"""

from __future__ import annotations

from gridironlabs.core.config import AppConfig, AppPaths
from gridironlabs.ui.overlays.grid_overlay import GridOverlayConfig
from gridironlabs.ui.pages.base_page import BasePage
from gridironlabs.ui.style.tokens import GRID


class SettingsPage(BasePage):
    """Settings page scaffold that owns a grid canvas."""

    def __init__(
        self,
        *,
        config: AppConfig,
        paths: AppPaths,
        overlay_config: GridOverlayConfig | None = None,
    ) -> None:
        resolved_overlay = overlay_config or GridOverlayConfig()
        super().__init__(cols=GRID.cols, rows=12, overlay_config=resolved_overlay)

        self.config = config
        self.paths = paths
        self.overlay_config = resolved_overlay
        self.setObjectName("page-settings")


__all__ = ["SettingsPage"]
