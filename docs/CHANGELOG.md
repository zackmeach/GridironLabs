# Changelog

## 2025-12-30

- OOTP-style panel chrome + standings scaffold:
  - `PanelChrome` now implements the multi-row header/body/footer chrome and provides an opinionated body API (`set_body`, `add_body`, `set_body_padding`).
  - Added `SectionBar` for in-body section headers/dividers.
  - Home page now includes a League Standings scaffold panel with division sections, aligned columns, and team logos.
  - Scrollbars are hidden globally (0px) while scrolling remains enabled (wheel/trackpad/keys).

## 2025-12-29

- Home dashboard layout:
  - (Later reset to scaffolds on 2025-12-30) Schedule region spans 10 columns on the right; standings/leaders consume the remaining width.
- Home schedule panel UX polish:
  - Team names render as full names, include team logos, and are clickable (navigates to the team summary page).
  - Scrollbars are hidden while scrolling remains enabled.
  - Week/date header text increased (24px) and row spacing increased (12px) for readability.
- Logo refresh workflow:
  - `scripts/refresh_data.py` now downloads team logos (via `NFLReadPyAdapter.fetch_teams`) and enriches `data/processed/teams.parquet` with `logo_path` / `logo_url` so the UI can render local images.
- Panel system prep (no visual/behavior change yet):
  - Introduced `PanelChrome` (`gridironlabs.ui.panels`) as the forward-looking page panel entrypoint.
  - Moved legacy panel chrome into a dedicated module and updated docs/imports accordingly.

## 2025-12-30

- Reset UI page bodies to scaffolds:
  - Removed the demo Home dashboard panels (standings/leaders/schedule) and the Settings demo panel so panel work can restart on the new system cleanly.

## 2025-12-28

- Added a schedule panel to the home page:
  - Displays a scrollable list of league games (upcoming or recent).
  - Positioned on the right side and full vertical height.
- Automated Team Logo extraction:
  - Updated `EntitySummary` model and `teams.parquet` schema to support `logo_url` and `logo_path`.
  - Implemented `fetch_teams` in `NFLReadPyAdapter` to download logos to `data/external/logos/`.
- Refactored panel chrome architecture:
  - Consolidated panel shells to enforce a unified UI contract.
  - Removed duplicated/fragmented panel implementations.

## 2025-12-19

- Documented current runtime behavior across README/architecture files (nav history, search handling, matchup ticker bootstrapping, and Parquet repository normalization/caching details).

## 2025-12-18

- Implemented entity navigation: clickable team/player names navigate to dedicated summary pages.
- Introduced `TeamSummaryPage` and `PlayerSummaryPage` as dedicated entity detail views.
- Refactored league leaders UI to a 3-column category layout matching the reference visual (Passing/Rushing, Receiving/Kicking, Defense).
- Enhanced standings UI with dark-themed division blocks to match the leaders styling.
- Added synthetic data generation controls to Settings (later removed when resetting page bodies to scaffolds).
- Improved synthetic data generation: added `receptions`, `tackles_for_loss`, and `punt_yards` to the player dataset.
- Increased header and link font sizes in `theme.qss` for better legibility (OOTP-style hierarchy).
- Isolated the panel header from the body layout and strictly enforced a consistent header structure.
- Removed header-actions support from the panel shell to maintain project-wide visual consistency.

## 2025-12-16

- Cleaned up UI scaffolding and QSS selector alignment (state panels now inherit `StatePanel` styling).
- Simplified Settings back to a minimal scaffold page.
- Hardened Parquet repository parsing (normalized optional fields, parsed ratings/stats, added schema-based column checks).
- Refreshed documentation to match current scaffolds and data dictionary fields.
- Fixed panel header layout: forced title to top-left and grouped header elements to prevent layout drift.
- Corrected header visibility check to use `isHidden()` instead of `isVisible()` (fixing headers hidden during initialization).
- Added link support to the panel header to enable optional top-right link text (e.g. "View All").

## 2025-12-15

- Introduced a reusable UI framework: `BasePage` → `GridCanvas` → panel chrome, plus a configurable debug grid overlay.
- Built a Settings page scaffold using the framework.
- Removed an earlier stopgap wrapper and replaced it with a real panel chrome component.

## 2025-12-12

- Introduced consistent panel chrome and restored component-specific title IDs to preserve hierarchy.
- Aligned League Leaders header back to a single-row title/season/action layout.
- Forced Debug Output terminal to true black background; Test 1 simulates log output on Execute.
- Removed pydarktheme layering; clarified dark-theme ownership in QSS and docs.
- Documented UI updates across README, architecture, and component nomenclature.

## 2025-12-11

- Added static Settings mock documentation and nomenclature.
- Updated context bar to meet height/icon requirements; adjusted panel title styling.
- Expanded data dictionary and added architecture diagram (text).
- Noted Windows dependency installs (PySide6, polars) in quickstart/docs.
