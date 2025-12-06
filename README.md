# GridironLabs

OOTP26-inspired NFL analytics explorer built with PySide6. This repository ships the project skeleton so you can begin implementing data ingestion, Parquet-backed storage, and UI features for players, teams, and coaches.

## Quickstart
- Install Python 3.10+ and create a virtualenv: `python -m venv .venv && source .venv/bin/activate`
- Install dependencies (plus dev tools): `pip install -e .[dev]`
- Launch the desktop shell: `python -m gridironlabs.main` (or `gridironlabs`)
- Expect a dark-themed shell with a persistent top nav. If Parquet datasets are present in `data/processed`, the UI uses them; otherwise it falls back to placeholders.
- (Optional) Generate synthetic-but-complete data: `python scripts/generate_fake_nfl_data.py --start-season 1999 --end-season 2025 --min-players 21000 --max-players 25000`

## Architecture
- `src/gridironlabs/core` — configuration, domain models, repository interfaces, logging wiring.
- `src/gridironlabs/data` — Parquet IO helpers plus source adapters for NFLreadpy and PFR scraping.
- `src/gridironlabs/services` — UI-facing services (search, summary retrieval).
- `src/gridironlabs/ui` — PySide6 windows/widgets; persistent top navigation bar, stacked content area, and reusable placeholder components.
- `src/gridironlabs/resources` — QSS dark theme and future assets.
- `data/` — Parquet-first storage (`raw`, `interim`, `processed`, `external`).
- `scripts/` — operational scripts (bootstrap placeholder included).
- `tests/` — reserved for unit/integration tests.

## Data workflow
1) Pull/generate base datasets via NFLreadpy or the synthetic generator (`scripts/generate_fake_nfl_data.py`).
2) (Planned) Augment with Pro-Football-Reference scraping where NFLreadpy lacks coverage.
3) Normalize and persist Parquet tables to `data/processed`.
4) UI reads Parquet via `gridironlabs.data.loaders` / `ParquetSummaryRepository` to populate summary pages and search.

## Next steps you can tackle
- Flesh out PFR scraping targets and caching.
- Define final Parquet schemas for players/teams/coaches and add validation.
- Ensure `ParquetSummaryRepository` stays aligned with Parquet schemas and handles partial/missing slices gracefully.
- Build UI tabs for home, players, teams, coaches, drafts, and comparisons.
- Add tests (pytest/pytest-qt) for services and widget smoke coverage.