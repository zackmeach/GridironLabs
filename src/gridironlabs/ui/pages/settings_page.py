"""Settings page scaffold.

Settings is currently a minimal page that owns a `BasePage` grid canvas. Real
settings panels can be added incrementally.
"""

from __future__ import annotations

from gridironlabs.core.config import AppConfig, AppPaths
from gridironlabs.ui.overlays.grid_overlay import GridOverlayConfig
from gridironlabs.ui.pages.base_page import BasePage
from gridironlabs.ui.panels import PanelChrome
from gridironlabs.ui.style.tokens import GRID
from gridironlabs.ui.widgets.base_components import AppCheckbox, AppComboBox
from gridironlabs.ui.widgets.form_grid import FormGrid
from gridironlabs.ui.widgets.tab_strip import TabStrip


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

        panel = PanelChrome(title="SETTINGS", panel_variant="card")

        # Body: settings-like form (OOTP panel 23 archetype).
        tabs = TabStrip([("play", "PLAY MODE"), ("ui", "UI")], initial="play")
        form = FormGrid()
        form.add_section("Play Mode")
        role = AppComboBox()
        role.addItem("General Manager")
        role.addItem("Coach")
        role.addItem("Commissioner")
        form.add_row(
            label="Your role",
            field=role,
            caption="Choose which role(s) you wish to take on. (Scaffolded settings UI.)",
        )
        form.add_row(label="Cannot be fired", field=AppCheckbox("Cannot be fired"))

        panel.add_body(tabs)
        panel.add_body(form, stretch=1)
        panel.set_footer_text("Settings are scaffolded; persistence is added for table surfaces first.")

        self.add_panel(panel, col=0, row=0, col_span=36, row_span=12)


__all__ = ["SettingsPage"]
