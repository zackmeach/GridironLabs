# Changelog

## 2025-12-29

- Home dashboard layout:
  - `SchedulePanel` spans 10 columns on the right; `HomeStandingsPanel` + `LeadersPanel` consume the remaining width.
- `SchedulePanel` UX polish:
  - Team names render as full names, include team logos, and are clickable (navigates to `TeamSummaryPage`).
  - Scrollbars are hidden while scrolling remains enabled.
  - Week/date header text increased (24px) and row spacing increased (12px) for readability.
- Logo refresh workflow:
  - `scripts/refresh_data.py` now downloads team logos (via `NFLReadPyAdapter.fetch_teams`) and enriches `data/processed/teams.parquet` with `logo_path` / `logo_url` so the UI can render local images.

## 2025-12-28

- Added `SchedulePanel` to the home page:
  - Displays a scrollable list of league games (upcoming or recent).
  - Positioned on the right side and full vertical height.
- Automated Team Logo extraction:
  - Updated `EntitySummary` model and `teams.parquet` schema to support `logo_url` and `logo_path`.
  - Implemented `fetch_teams` in `NFLReadPyAdapter` to download logos to `data/external/logos/`.
- Refactored `PanelCard` architecture:
  - Moved `PanelCard` to `base_components.py` as the single parent class for all containers.
  - `Card` and `_BaseStatePanel` now inherit from `PanelCard`, enforcing a unified UI contract.
  - Removed duplicated/fragmented panel implementations.

## 2025-12-19

- Documented current runtime behavior across README/architecture files (nav history, search handling, matchup ticker bootstrapping, and Parquet repository normalization/caching details).

## 2025-12-18

- Implemented entity navigation: team names and player names in the UI (standings, leaders) are now clickable and navigate to dedicated summary pages.
- Introduced `TeamSummaryPage` and `PlayerSummaryPage` as dedicated entity detail views.
- Refactored `LeadersPanel` to a 3-column category layout matching the reference visual (Passing/Rushing, Receiving/Kicking, Defense).
- Enhanced `HomeStandingsPanel` with dark-themed division blocks to match the `LeadersPanel` styling.
- Added `DataGenerationPanel` to the Settings page to centralize synthetic data controls.
- Improved synthetic data generation: added `receptions`, `tackles_for_loss`, and `punt_yards` to the player dataset.
- Increased header and link font sizes in `theme.qss` for better legibility (OOTP-style hierarchy).
- Isolated `PanelCard` header stack from the body layout and strictly enforced a Title (Left) / Link (Right) / Separator (Below) structure.
- Removed `header_actions` support from `PanelCard` to maintain project-wide visual consistency.

## 2025-12-16

- Cleaned up UI scaffolding and QSS selector alignment (state panels now inherit `StatePanel` styling).
- Simplified Settings back to a minimal scaffold page.
- Hardened Parquet repository parsing (normalized optional fields, parsed ratings/stats, added schema-based column checks).
- Refreshed documentation to match current scaffolds and data dictionary fields.
- Fixed `PanelCard` header layout: forced title to top-left and grouped separator directly beneath it (preventing layout drift).
- Corrected `PanelCard` header visibility check to use `isHidden()` instead of `isVisible()` (fixing headers hidden during initialization).
- Added `set_link()` to `PanelCard` to support optional top-right link text (e.g. "View All").

## 2025-12-15

- Introduced a reusable UI framework: `BasePage` → `GridCanvas` → `PanelCard`, plus a configurable debug grid overlay.
- Built a Settings page scaffold using the framework.
- Removed the legacy `PanelCard` compatibility wrapper and replaced it with a real `PanelCard` component.

## 2025-12-12

- Introduced `PanelCard` for consistent panel chrome (optional title + white separator) and restored component-specific title IDs to preserve hierarchy.
- Aligned League Leaders header back to a single-row title/season/action layout.
- Forced Debug Output terminal to true black background; Test 1 simulates log output on Execute.
- Removed pydarktheme layering; clarified dark-theme ownership in QSS and docs.
- Documented UI updates across README, architecture, and component nomenclature.

## 2025-12-11

- Added static Settings mock documentation and nomenclature.
- Updated context bar to meet height/icon requirements; added panel title separators.
- Expanded data dictionary and added architecture diagram (text).
- Noted Windows dependency installs (PySide6, polars) in quickstart/docs.
