# GridironLabs

OOTP26-inspired NFL analytics explorer built with PySide6. This repository ships the project skeleton so you can begin implementing data ingestion, Parquet-backed storage, and UI features for players, teams, and coaches.

## Quickstart

- Install Python 3.11+ and create a virtualenv  
  - macOS/Linux: `python -m venv .venv && source .venv/bin/activate`  
  - Windows: `python -m venv .venv && .\\.venv\\Scripts\\activate`
- Install dependencies (plus dev tools): `pip install -e .[dev]`
- If PySide6 or polars are missing (common on fresh Windows setups), add:  
  `pip install pyside6 polars`
- (Optional) Generate synthetic Parquet so the UI has data (players/teams/coaches/games with schedules and scores): `python scripts/generate_fake_nfl_data.py`
- Launch the desktop shell: `python -m gridironlabs.main`, the `gridironlabs` console script, or `python main.py`.
- You should see a dark-themed shell with a persistent top nav (cycling upcoming matchups from `games.parquet`), stacked content, and a Home page with an OOTP-style **League Leaders** grid. The Settings page now mirrors the provided mock with cosmetic panels for Data Generation, UI Grid Layout, Test Cases, and Debug Output.
- If `nflreadpy` is unavailable, the app shows an offline placeholder banner and continues with stub data.
- Run smoke tests (includes pytest-qt UI check): `pytest`

## Architecture

- `src/gridironlabs/core` — configuration, domain models, repository interfaces, logging wiring.
- `src/gridironlabs/data` — Parquet IO helpers plus source adapters for NFLreadpy and PFR scraping; schemas now include games (schedules + outcomes).
- `src/gridironlabs/services` — UI-facing services (search, summary retrieval).
- `src/gridironlabs/ui` — PySide6 windows/widgets; persistent top navigation bar (with rotating matchup ticker), stacked content area, a League Leaders home grid, and a static Settings mock matching the shared reference layout.
- `src/gridironlabs/resources` — QSS dark theme and future assets.
- `data/` — Parquet-first storage (`raw`, `interim`, `processed`, `external`); processed data includes players, teams, coaches, and games.
- `scripts/` — operational scripts (bootstrap placeholder included).
- `tests/` — reserved for unit/integration tests.

## Data workflow

1) Pull/generate base datasets via NFLreadpy or the synthetic generator (`scripts/generate_fake_nfl_data.py`) — players, teams, coaches, and games (regular season + postseason rounds). The UI ticker reads from `games.parquet`.
2) (Planned) Augment with Pro-Football-Reference scraping where NFLreadpy lacks coverage.
3) Normalize and persist Parquet tables to `data/processed`.
4) UI reads Parquet via `gridironlabs.data.loaders` / `ParquetSummaryRepository` to populate summary pages, search, and schedule-aware views.

## Next steps you can tackle

- Flesh out PFR scraping targets and caching.
- Define final Parquet schemas for players/teams/coaches and add validation.
- Ensure `ParquetSummaryRepository` stays aligned with Parquet schemas and handles partial/missing slices gracefully.
- Expand the Home dashboard beyond the League Leaders grid (e.g., standings, news ticker).
- Build UI tabs for players, teams, coaches, drafts, and comparisons.
- Add tests (pytest/pytest-qt) for services and widget smoke coverage.
