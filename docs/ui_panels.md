# UI Panels Framework

This project uses a reusable **Page → GridCanvas → PanelCard** pattern for building screens.

## Concepts

- **Page (BasePage)**: owns the content region below the context bar.
- **GridCanvas**: a 24-column grid used to place panels by `(col, row, col_span, row_span)`.
- **PanelCard**: consistent panel chrome (optional header title, optional header-right actions, separator, padded body).
  - The header stack is isolated from the body to ensure consistent layout regardless of content.

- **GridOverlay**: an optional debug overlay for the grid canvas, controlled by a `GridOverlayConfig`.

## Create a new page

1) Create a page class that inherits `BasePage`.
2) Create `PanelCard` instances (or small panel subclasses).
3) Place panels on the grid with `add_panel(...)`.

Example:

```python
from PySide6.QtWidgets import QLabel

from gridironlabs.ui.overlays.grid_overlay import GridOverlayConfig
from gridironlabs.ui.pages.base_page import BasePage
from gridironlabs.ui.widgets.panel_card import PanelCard


class MyPage(BasePage):
    def __init__(self, *, overlay_config: GridOverlayConfig | None = None) -> None:
        super().__init__(cols=24, rows=12, overlay_config=overlay_config)
        self.setObjectName("page-my")

        panel = PanelCard("My Panel")
        panel.body_layout.addWidget(QLabel("Hello"))

        # Place at col 0..11 (half width), row 0..5 (half height)
        self.add_panel(panel, col=0, row=0, col_span=12, row_span=6)
```

## Enable the debug grid overlay

Create a shared `GridOverlayConfig` and pass it into your pages:

```python
from gridironlabs.ui.overlays.grid_overlay import GridOverlayConfig

config = GridOverlayConfig()

page = MyPage(overlay_config=config)

config.set_enabled(True)
config.set_opacity(0.2)
config.set_color_hex("#2563eb")
config.set_cell_size(28)
```

## Reference implementation

- **HomePage** implements the dashboard using several framework components:
  - `HomeStandingsPanel`: A custom panel for conference/division standings.
  - `LeadersPanel`: A 3-column category grid for league leaders.
- **SettingsPage** uses the framework to host:
  - `DataGenerationPanel`: A dedicated panel for synthetic data pipeline controls.
- **Entity Pages**:
  - `TeamSummaryPage` and `PlayerSummaryPage` serve as summary scaffolds for detail views.
