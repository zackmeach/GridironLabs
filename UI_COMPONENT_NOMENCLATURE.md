# UI Component Nomenclature

Current UI primitives and screens (cosmetic unless noted):

- **GridironLabsMainWindow** — main shell; hosts top navigation, page context bar, and stacked pages.
- **NavigationBar** — top nav strip with back/forward, home, section buttons, rotating context/ticker, search box, and settings button.
- **PageContextBar** — bar under the nav showing title, subtitle, and stat chips for the active page.
- **HomePage** — home page scaffold; body content is intentionally empty (everything below the context bar).
- **SectionPage** — section page scaffold for sections (Seasons, Teams, Players, Drafts, History); body content intentionally empty.
- **SearchResultsPage** — search page scaffold; body content intentionally empty.
- **BasePage** — reusable page base that owns a `GridCanvas` for panel placement.
- **GridCanvas** — 24-column content grid; panels are placed by `(col, row, col_span, row_span)`.
- **GridOverlay / GridOverlayConfig** — optional debug overlay for the grid (toggle, opacity, color, cell size).
- **PanelCard** — consistent panel chrome (title, header actions, separator, padded body).
- **SettingsPage** — example page implemented with the panel framework (Data Generation, UI Grid Layout, Test Cases, Debug Output).
- **Card** — reusable card shell with optional title, enforced chrome, and a `card-role` property for variants (available for future pages; currently used by `league_leaders.py`).
- **AppSwitch** — custom painted on/off switch control (available).
- **AppCheckbox / AppSlider / AppLineEdit / AppSpinBox / AppComboBox** — shared controls with enforced object names for consistent styling.
- **StatusBanner** — inline banner for offline/error/info notices (available).
- **LoadingPanel / EmptyPanel / ErrorPanel** — state placeholders (available).
- **LeadersPanel** — League Leaders container with inline title/season label/action in one header row (available; currently not mounted in `HomePage`).
  - **LeaderSection** — category column (Passing, Receiving, Defense, Rushing, Kicking & Punting) using its own title style.
  - **LeaderCard** — stat card listing top entries with its own title style.

Supporting assets:

- **theme.qss** — dark theme styling these components.
- **main_logo.png** — logo used in the context bar icon slot.
