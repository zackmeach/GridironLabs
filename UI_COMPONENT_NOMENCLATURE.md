# UI Component Nomenclature

Current UI primitives and screens (cosmetic unless noted):

- **GridironLabsMainWindow** — main shell; hosts top navigation, page context bar, and stacked pages.
- **NavigationBar** — top nav strip with back/forward, home, section buttons, rotating context/ticker, search box, and settings button.
- **PageContextBar** — bar under the nav showing title, subtitle, and stat chips for the active page.
- **HomePage** — dashboard page; contains **LeadersPanel** (League Leaders grid).
- **SectionPage** — generic placeholder pages for sections (Seasons, Teams, Players, Drafts, History).
- **SearchResultsPage** — search results placeholder page.
- **SettingsPage** — static mock matching the provided reference; four panels with a 4/3/3 width split:
  - **Data Generation** (season range combos, toggles for Real Data / Pull NFLverse / Pull Pro-Football-Reference, Generate Data checkboxes, Player Types checkboxes, last-update table, full-width Generate Data button)
  - **UI Grid Layout** (Enable Grid toggle, Opacity slider, Color swatch + hex input, Cell Size spinbox)
  - **Test Cases** (three toggles, Execute Tests button)
  - **Debug Output** (terminal-like text area)
- **ToggleSwitch** — custom painted on/off switch used across Settings.
- **StatusBanner** — inline banner for offline/error/info notices.
- **LoadingPanel / EmptyPanel / ErrorPanel** — state placeholders.
- **LeadersPanel** — League Leaders container.
  - **LeaderSection** — category column (Passing, Receiving, Defense, Rushing, Kicking & Punting).
  - **LeaderCard** — stat card listing top entries.

Supporting assets:
- **theme.qss** — dark theme styling these components.
- **main_logo.png** — logo used in Settings header.

