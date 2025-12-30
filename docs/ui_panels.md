# UI Panels Framework

This project uses a reusable **Page → GridCanvas → PanelChrome** pattern for building screens.

## Concepts

- **Page (BasePage)**: owns the content region below the context bar.
- **GridCanvas**: a 36-column grid used to place panels by `(col, row, col_span, row_span)`.
- **PanelChrome**: the page-panel container used on the grid.
  - Implemented as an **OOTP-style vertical stack**:
    - Primary header (title + actions)
    - Secondary header (optional controls)
    - Tertiary header (optional column semantics / sort row)
    - Body (content)
    - Footer (optional meta)
  - Body content should be managed via the `PanelChrome` API (`set_body`, `add_body`, `clear_body`).
  - For table-like surfaces, prefer `PanelChrome(..., panel_variant="table")` so body padding defaults to 0 (rows align tightly under the header).
  - If you need a one-off override, use `set_body_padding(...)`.

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
        super().__init__(cols=36, rows=12, overlay_config=overlay_config)
        self.setObjectName("page-my")

        panel = PanelChrome(title="MY PANEL")
        panel.set_body(QLabel("Hello"))

        # Place at col 0..11 (half width), row 0..5 (half height)
        self.add_panel(panel, col=0, row=0, col_span=18, row_span=6)
```

## Where the OOTP-style panel work lives

- **Design contract**: see the repo root `recommendation.txt` (metrics, semantics, persistence, composition rules).
- **New panel system**: `gridironlabs.ui.panels` (starting with `PanelChrome`).
- **Implementation detail**: a temporary legacy implementation is retained internally for compatibility until the migration completes.

## Scroll behavior (no visible scrollbars)

The theme supports an OOTP-style “no visible scrollbars” mode without forcing it globally.

- **Default**: platform scrollbars remain available (important for future `QTableView` / large tables).
- **OOTP-style hidden scrollbars**: set `scrollVariant="hidden"` on a specific `QAbstractScrollArea` (e.g. a `QScrollArea`), and keep scroll policies as `AsNeeded` so scrolling stays enabled (wheel/trackpad/keys).

Example:

```python
scroll_area.setProperty("scrollVariant", "hidden")
scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
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

- **HomePage** includes a League Standings scaffold panel as a reference surface for the chrome + dense rows.
- **SettingsPage** is intentionally a blank scaffold while the new panel system is implemented.
- **Entity Pages**:
  - `TeamSummaryPage` and `PlayerSummaryPage` serve as summary scaffolds for detail views.
