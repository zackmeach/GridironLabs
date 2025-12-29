"""Settings page scaffold.

Settings is currently a minimal page that owns a `BasePage` grid canvas. Real
settings panels can be added incrementally.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel
from gridironlabs.core.config import AppConfig, AppPaths
from gridironlabs.ui.overlays.grid_overlay import GridOverlayConfig
from gridironlabs.ui.pages.base_page import BasePage
from gridironlabs.ui.style.tokens import GRID
from gridironlabs.ui.widgets.data_generation import DataGenerationPanel


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

        # Data Generation Panel
        self.data_gen_panel = DataGenerationPanel()
        
        # Add to grid: 1/2 horizontal (18/36 cols), full vertical (12/12 rows)
        self.add_panel(self.data_gen_panel, col=0, row=0, col_span=18, row_span=12)


__all__ = ["SettingsPage"]
