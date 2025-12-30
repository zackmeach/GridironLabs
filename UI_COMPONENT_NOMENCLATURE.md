# UI Component Nomenclature

Current UI primitives and screens (cosmetic unless noted):

- **GridironLabsMainWindow** — main shell; hosts top navigation, page context bar, and stacked pages.
- **NavigationBar** — top nav strip with back/forward, home, section buttons, rotating context/ticker, search box, and settings button.
- **PageContextBar** — bar under the nav showing title, subtitle, and stat chips for the active page.
- **HomePage** — home dashboard scaffold (content intentionally empty while the new panel system is implemented).
- **TeamSummaryPage** — dedicated summary page for team details (rosters, schedules).
- **PlayerSummaryPage** — dedicated summary page for player details (stats, ratings).
- **SectionPage** — section page scaffold for sections (Seasons, Teams, Players, Drafts, History); body content intentionally empty.
- **SearchResultsPage** — search page scaffold; body content intentionally empty.
- **BasePage** — reusable page base that owns a `GridCanvas` for panel placement.
- **GridCanvas** — 24-column content grid; panels are placed by `(col, row, col_span, row_span)`.
- **GridOverlay / GridOverlayConfig** — optional debug overlay for the grid (toggle, opacity, color, cell size).
- **PanelChrome** — page panel container used on the grid (currently a minimal box + `body_layout`; richer chrome comes later).
  - Currently implemented as a compatibility wrapper while the new slot-based bars are implemented incrementally.
- **SettingsPage** — settings scaffold (content intentionally empty while the new panel system is implemented).

Supporting assets:

- **theme.qss** — dark theme styling these components.
- **main_logo.png** — logo used in the context bar icon slot.
