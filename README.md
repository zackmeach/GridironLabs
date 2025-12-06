# GridironLabs

OOTP26-inspired NFL analytics explorer built with PySide6. This repository ships the project skeleton so you can begin implementing data ingestion, Parquet-backed storage, and UI features for players, teams, and coaches.

## Quickstart
- Install Python 3.10+ and create a virtualenv: `python -m venv .venv && source .venv/bin/activate`
- Install dependencies (plus dev tools): `pip install -e .[dev]`
- Launch the desktop shell: `python -m gridironlabs.main` (or `gridironlabs`)
- Expect a dark-themed shell with a persistent top nav and placeholder pages; if `nflreadpy` is missing the app starts in offline placeholder mode.
- (Optional) Scaffold data pulls: `python scripts/bootstrap_data.py`

## Architecture
- `src/gridironlabs/core` — configuration, domain models, repository interfaces, logging wiring.
- `src/gridironlabs/data` — Parquet IO helpers plus source adapters for NFLreadpy and PFR scraping.
- `src/gridironlabs/services` — UI-facing services (search, summary retrieval).
- `src/gridironlabs/ui` — PySide6 windows/widgets; persistent top navigation bar, stacked content area, and reusable placeholder components.
- `src/gridironlabs/resources` — QSS dark theme and future assets.
- `data/` — Parquet-first storage (`raw`, `interim`, `processed`, `external`).
- `scripts/` — operational scripts (bootstrap placeholder included).
- `tests/` — reserved for unit/integration tests.

## Data workflow (planned)
1) Pull base datasets via NFLreadpy (`scripts/bootstrap_data.py`).
2) Augment with Pro-Football-Reference scraping where NFLreadpy lacks coverage.
3) Normalize and persist Parquet tables to `data/processed`.
4) UI reads Parquet via `gridironlabs.data.loaders` to populate summary pages and comparisons.

## Next steps you can tackle
- Flesh out PFR scraping targets and caching.
- Define final Parquet schemas for players/teams/coaches and add validation.
- Replace the in-memory repository with a Parquet-backed implementation.
- Build UI tabs for home, players, teams, coaches, drafts, and comparisons.
- Add tests (pytest/pytest-qt) for services and widget smoke coverage.