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

## Panel cookbook (agent checklist)

This section is intentionally written so an independent agent can add a new panel (e.g. “Player Leaderboards”) without drifting from the OOTP-style contract.

### 1) Decide what you’re building (where code should live)

- **Page composition** (layout + wiring): `src/gridironlabs/ui/pages/*` (or `ui/main_window.py` for the current HomePage reference surface).
- **Reusable panel bodies** (tables/lists/forms): `src/gridironlabs/ui/widgets/*`.
  - Example reference: `src/gridironlabs/ui/widgets/standings.py`
- **Panel primitives only** (chrome + bars): `src/gridironlabs/ui/panels/*`.
  - Do **not** build “feature panels” here unless it’s a reusable archetype primitive.
- **Assets** (logos/icons helpers): `src/gridironlabs/ui/assets/*`.
  - Example reference: `src/gridironlabs/ui/assets/logos.py`
- **Styling**: `src/gridironlabs/resources/theme.qss` (avoid inline `setStyleSheet`).

### 2) Choose a panel variant (density + padding)

- Use `PanelChrome(..., panel_variant="table")` for dense, table-like surfaces (standings, leaderboards, lists).
  - Body padding defaults to 0 so content aligns tightly under header bars.
- Use `panel_variant="card"` for padded, “card content” panels (forms, summaries, text blocks).

### 3) Build the chrome first, then the body

- **Primary header**: title on the left, optional actions on the right.
  - Use `panel.add_action_right(widget)` for right-side actions.
  - Use `panel.add_action_left(widget)` for left-side controls (after the title).
- **Secondary header** (filters/paging): use `panel.set_filters_left(*widgets)` / `panel.set_filters_right(*widgets)`.
- **Tertiary header** (column semantics / sort row): use `panel.set_columns_left(*widgets)` / `panel.set_columns_right(*widgets)`.
- **Important invariant**: don’t manually manage bar visibility in most cases.
  - Bars auto-show when you add content, and `clear()` hides empty bars.
  - If you need to rebuild filters/actions dynamically, use:
    - `panel.clear_filters()`
    - `panel.clear_columns()`

### Secondary header: OOTP-style filter rows

The **secondary header** is the canonical place for OOTP-style filter rows. In most cases you can use compact `QComboBox`-style controls without extra labels (the selected text acts as the label), and optionally add tooltips for clarity.

Reference implementation (Home → **League Leaders** filter row):
- `src/gridironlabs/ui/widgets/leaders_filters.py` (`LeadersFilterBar`)
- `src/gridironlabs/core/nfl_structure.py` (static team→conference/division mapping used for filtering)

Notes:
- Conference/division/team filtering is supported via the static NFL mapping.
- Age/rookie filters are scaffolded but disabled until player age metadata is added to the dataset.

### 4) Table/list surfaces: use a shared ColumnSpec (no drift)

If your body renders rows aligned under a header row, define one shared column spec list and generate both header cells and row cells from it.

Reference implementation:
- `STANDINGS_COLUMNS` in `src/gridironlabs/ui/widgets/standings.py`

### 5) Styling rules (avoid drift)

- **Do not** call `setStyleSheet(...)` on panel archetype widgets.
- Set `objectName` / dynamic properties and style once in QSS.
- Keep typography/density consistent with the existing panel selectors (see `theme.qss`).

### 6) Scrolling rules (OOTP feel without breaking future tables)

- Default: keep platform scrollbars.
- For OOTP-style “no visible scrollbars” on a specific list/table surface:
  - prefer `make_locked_scroll(widget)` which sets `scrollVariant="hidden"` + `AsNeeded` policies and installs `MicroScrollGuard` to treat <= 1px overflow as “fits”
  - for QTableView surfaces (`OOTPTableView`), keep platform scrollbars unless the page explicitly opts into hidden scrollbars

### 7) Interactivity rules (rows should be actionable)

- Prefer passing callbacks from the Page into the body widget (e.g. `on_player_click`, `on_team_click`).
- Make row widgets the click target (set child labels `WA_TransparentForMouseEvents=True` so clicks hit the row).

### 8) Testing expectations (keep invariants enforced)

- Add/extend pytest-qt tests when introducing new UI invariants or click navigation.
- Reference tests:
  - `tests/ui/test_panel_system.py`

## Example: Player Leaderboards panel (agent-safe skeleton)

This example shows the intended file split and API usage (chrome + shared ColumnSpec + scroll variant + click callbacks).

```python
# src/gridironlabs/ui/widgets/player_leaderboards.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget


from gridironlabs.ui.table.columns import ColumnSpec


LEADERBOARD_COLUMNS: tuple[ColumnSpec, ...] = (
    ColumnSpec("rank", "#", 40, Qt.AlignRight | Qt.AlignVCenter),
    ColumnSpec("name", "PLAYER", 240, Qt.AlignLeft | Qt.AlignVCenter),
    ColumnSpec("value", "YDS", 80, Qt.AlignRight | Qt.AlignVCenter),
)


class PlayerLeaderboardsHeaderRow(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PlayerLeaderboardsHeaderRow")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # bar padding controls inset
        layout.setSpacing(4)

        for col in LEADERBOARD_COLUMNS:
            cell = QLabel(col.label)
            cell.setObjectName("PlayerLeaderboardsHeaderCell")
            cell.setFixedWidth(col.width)
            cell.setAlignment(col.alignment)
            layout.addWidget(cell)
        layout.addStretch(1)


class PlayerLeaderboardsWidget(QFrame):
    def __init__(self, *, on_player_click: Callable[[str], None] | None = None) -> None:
        super().__init__()
        self.setObjectName("PlayerLeaderboardsWidget")
        self._on_player_click = on_player_click

        from gridironlabs.ui.widgets.scroll_guard import make_locked_scroll

        self.content = QWidget()
        self.content.setObjectName("PlayerLeaderboardsContent")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.scroll = make_locked_scroll(self.content, threshold_px=1)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.scroll)

    def add_row(self, *, player_name: str, value: str, rank: str) -> None:
        # In real code: create a row widget with hover + click -> self._on_player_click(player_name)
        row = QLabel(f"{rank}  {player_name}  {value}")
        row.setObjectName("PlayerLeaderboardsRow")
        self.content_layout.addWidget(row)
```

```python
# Page composition (example): add the panel to a Page/HomePage
from PySide6.QtWidgets import QLabel

from gridironlabs.ui.panels import PanelChrome
from gridironlabs.ui.widgets.player_leaderboards import (
    PlayerLeaderboardsHeaderRow,
    PlayerLeaderboardsWidget,
)

panel = PanelChrome(title="PLAYER LEADERBOARDS", panel_variant="table")

# Optional: filters/paging in secondary header (auto-shows)
panel.set_filters_left(QLabel("SEASON: 2025"))

# Column semantics in tertiary header
panel.set_columns_left(PlayerLeaderboardsHeaderRow())

body = PlayerLeaderboardsWidget(on_player_click=self._on_player_click)
panel.set_body(body)

body.add_row(rank="1", player_name="Player A", value="5,123")
body.add_row(rank="2", player_name="Player B", value="4,980")
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

- **HomePage** includes **League Standings** and **League Leaders** as reference surfaces for the chrome + dense rows (leaders supports clickable stat headers that re-rank best-to-worst per category).
- **SettingsPage** is intentionally a blank scaffold while the new panel system is implemented.
- **Entity Pages**:
  - `TeamSummaryPage` and `PlayerSummaryPage` serve as summary scaffolds for detail views.
