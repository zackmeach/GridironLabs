# UI Panels Framework

This project uses a reusable **Page → GridCanvas → PanelChrome** pattern for building screens.

## Concepts

- **Page (BasePage)**: owns the content region below the context bar.
- **GridCanvas**: a 36-column grid used to place panels by `(col, row, col_span, row_span)`.
- **PanelChrome**: the page-panel container used on the grid.
  - Currently implemented as a **minimal box** with the panel background color and a single `body_layout`.
  - The richer OOTP-style chrome (slot-based bars, section bars, etc.) will be built on top of this later.

- **GridOverlay**: an optional debug overlay for the grid canvas, controlled by a `GridOverlayConfig`.

## Create a new page

1) Create a page class that inherits `BasePage`.
2) Create `PanelChrome` instances (or small panel subclasses).
3) Place panels on the grid with `add_panel(...)`.

Example:

```python
from PySide6.QtWidgets import QLabel

from gridironlabs.ui.overlays.grid_overlay import GridOverlayConfig
from gridironlabs.ui.pages.base_page import BasePage
from gridironlabs.ui.panels import PanelChrome


class MyPage(BasePage):
    def __init__(self, *, overlay_config: GridOverlayConfig | None = None) -> None:
        super().__init__(cols=24, rows=12, overlay_config=overlay_config)
        self.setObjectName("page-my")

        panel = PanelChrome()
        panel.body_layout.addWidget(QLabel("Hello"))

        # Place at col 0..11 (half width), row 0..5 (half height)
        self.add_panel(panel, col=0, row=0, col_span=12, row_span=6)
```

## Where the OOTP-style panel work lives

- **Design contract**: see the repo root `recommendation.txt` (metrics, semantics, persistence, composition rules).
- **New panel system**: `gridironlabs.ui.panels` (starting with `PanelChrome`).
- **Implementation detail**: a temporary legacy implementation is retained internally for compatibility until the migration completes.

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

- **HomePage** is intentionally a blank scaffold while the new panel system is implemented.
- **SettingsPage** is intentionally a blank scaffold while the new panel system is implemented.
- **Entity Pages**:
  - `TeamSummaryPage` and `PlayerSummaryPage` serve as summary scaffolds for detail views.
