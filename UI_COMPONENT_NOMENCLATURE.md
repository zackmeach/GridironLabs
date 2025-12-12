# UI Component Nomenclature

Current UI primitives and screens (cosmetic unless noted):

- **GridironLabsMainWindow** — main shell; hosts top navigation, page context bar, and stacked pages.
- **NavigationBar** — top nav strip with back/forward, home, section buttons, rotating context/ticker, search box, and settings button.
- **PageContextBar** — bar under the nav showing title, subtitle, and stat chips for the active page.
- **HomePage** — dashboard page; contains **LeadersPanel** (League Leaders grid).
- **SectionPage** — generic placeholder pages for sections (Seasons, Teams, Players, Drafts, History).
- **SearchResultsPage** — search results placeholder page.
- **SettingsPage** — static mock matching the provided reference; four panels (all on `PanelCard` chrome) with a 4/3/3 width split:
  - **Data Generation** (season range combos, toggles for Real Data / Pull NFLverse / Pull Pro-Football-Reference, section headers for Generate Data and Player Types checkboxes, last-update table, full-width Generate Data button)
  - **UI Grid Layout** (Enable Grid toggle, Opacity slider, Color swatch + hex input, Cell Size spinbox)
  - **Test Cases** (three toggles, Execute Tests button; Test 1 triggers simulated terminal output)
  - **Debug Output** (terminal-like text area with forced black background and no wrapping)
- **ToggleSwitch** — custom painted on/off switch used across Settings.
- **StatusBanner** — inline banner for offline/error/info notices.
- **LoadingPanel / EmptyPanel / ErrorPanel** — state placeholders.
- **PanelCard** — shared panel shell (optional title + white separator + body layout) used across settings panels and leaderboard components.
- **LeadersPanel** — League Leaders container with inline title/season label/action in one header row.
  - **LeaderSection** — category column (Passing, Receiving, Defense, Rushing, Kicking & Punting) using its own title style.
  - **LeaderCard** — stat card listing top entries with its own title style.

Supporting assets:

- **theme.qss** — dark theme styling these components.
- **main_logo.png** — logo used in Settings header.
