# UI Component Nomenclature

Current UI primitives and screens (cosmetic unless noted):

- **GridironLabsMainWindow** — main shell; hosts top navigation, page context bar, and stacked pages.
- **NavigationBar** — top nav strip with back/forward, home, section buttons, rotating context/ticker, search box, and settings button.
- **PageContextBar** — bar under the nav showing title, subtitle, and stat chips for the active page.
- **HomePage** — home dashboard with OOTP-style panels:
  - **League Standings** panel (division sections; rows clickable → team summary)
  - **League Leaders** panel (category sections; clickable stat headers → re-rank best-to-worst; rows clickable → player summary)
- **TeamSummaryPage** — dedicated summary page for team details (rosters, schedules).
- **PlayerSummaryPage** — dedicated summary page for player details (stats, ratings).
- **SectionPage** — section page scaffold for sections (Seasons, Teams, Players, Drafts, History); body content intentionally empty.
- **SearchResultsPage** — search page scaffold; body content intentionally empty.
- **BasePage** — reusable page base that owns a `GridCanvas` for panel placement.
- **GridCanvas** — 36-column content grid; panels are placed by `(col, row, col_span, row_span)`.
- **GridOverlay / GridOverlayConfig** — optional debug overlay for the grid (toggle, opacity, color, cell size).
- **PanelChrome** — OOTP-style page panel container used on the grid.
  - Vertical stack: primary/secondary/tertiary header bars + body + optional footer.
  - `panel_variant="table"` provides dense “table/list” padding defaults for aligned rows.
- **SettingsPage** — settings reference surface (TabStrip + FormGrid) implemented as a `PanelChrome` card panel.
- **TableDemoPage** — dev-only high-row-count table surface used to validate `OOTPTableView` styling/sorting/persistence.

Reusable primitives (selected):
- **CompactFilterBar** — standard single-row toolbar/filter strip used in the secondary header.
- **KeyValueList** — striped key/value table rows for detail panels; supports value widgets.
- **RatingBarRow** — single/dual rating bars for current/potential style panels.
- **OOTPTableView** — QTableView wrapper with proxy sorting and QSettings persistence.

Supporting assets:

- **theme.qss** — dark theme styling these components.
- **main_logo.png** — logo used in the context bar icon slot.
