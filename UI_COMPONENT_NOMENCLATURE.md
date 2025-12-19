# UI Component Nomenclature

Current UI primitives and screens (cosmetic unless noted):

- **GridironLabsMainWindow** — main shell; hosts top navigation, page context bar, and stacked pages.
- **NavigationBar** — top nav strip with back/forward, home, section buttons, rotating context/ticker, search box, and settings button.
- **PageContextBar** — bar under the nav showing title, subtitle, and stat chips for the active page.
- **HomePage** — home dashboard containing `HomeStandingsPanel` and `LeadersPanel`.
- **TeamSummaryPage** — dedicated summary page for team details (rosters, schedules).
- **PlayerSummaryPage** — dedicated summary page for player details (stats, ratings).
- **SectionPage** — section page scaffold for sections (Seasons, Teams, Players, Drafts, History); body content intentionally empty.
- **SearchResultsPage** — search page scaffold; body content intentionally empty.
- **BasePage** — reusable page base that owns a `GridCanvas` for panel placement.
- **GridCanvas** — 24-column content grid; panels are placed by `(col, row, col_span, row_span)`.
- **GridOverlay / GridOverlayConfig** — optional debug overlay for the grid (toggle, opacity, color, cell size).
- **PanelCard** — consistent panel chrome (title top-left, link top-right, separator below, padded body).
- **SettingsPage** — hosts the `DataGenerationPanel` and other configuration views.
- **HomeStandingsPanel** — conference/division standings with clickable team navigation.
- **LeadersPanel** — 3-column league leaders grid with clickable player/team navigation.
  - **LeaderSection** — category column (Passing, Receiving, Defense, Rushing, Kicking & Punting) using its own title style.
  - **LeaderCard** — stat card listing top entries with its own title style and clickable player/team links.
- **DataGenerationPanel** — centralized controls for synthetic data generation in Settings.
- **Card** — reusable card shell with optional title, enforced chrome, and a `card-role` property for variants.

Supporting assets:

- **theme.qss** — dark theme styling these components.
- **main_logo.png** — logo used in the context bar icon slot.
