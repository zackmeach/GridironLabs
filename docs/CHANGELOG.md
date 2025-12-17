# Changelog

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
