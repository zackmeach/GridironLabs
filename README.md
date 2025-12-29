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
- You should see a dark-themed shell with a persistent top nav (cycling upcoming matchups from `games.parquet`), a 2x-height context bar with stat chips, and stacked pages. Home dashboard features conference/division standings and a 3-column league leaders grid with clickable player/team links. Back/forward controls mirror a browser-style history for page navigation.
- Click on team names or player names in the home dashboard to navigate to dedicated summary detail pages. Search submissions route to a placeholder results page while logging queries.
- If `data/processed` is empty or Parquet fails validation, the app still boots and the context bar will reflect a zero-count/validation status; the matchup ticker may have no items. Seed Parquet with `python scripts/generate_fake_nfl_data.py` if you want matchups and leaders to appear.
- Run smoke tests (includes pytest-qt UI check): `pytest`

## Architecture

- `src/gridironlabs/core` — configuration, domain models, repository interfaces, logging wiring. Environment variables are loaded from `.env` when present and directories are created on boot.
- `src/gridironlabs/data` — Parquet IO helpers plus source adapters for NFLreadpy and PFR scraping; schemas now include games (schedules + outcomes). The default repository normalizes stats/ratings, caches tables in memory, and will surface schema/IO issues via typed errors.
- `src/gridironlabs/services` — UI-facing services (search, summary retrieval).
- `src/gridironlabs/ui` — PySide6 windows/widgets; persistent top navigation bar (with rotating matchup ticker), a 2x-height context bar with the page title/subtitle/stats, and stacked pages. Page titles render only in the context bar. Navigation history (back/forward), settings, and search hooks are wired up; seasons/teams/players/drafts/history pages are scaffolded while team/player summaries render when triggered from Home.
- `src/gridironlabs/resources` — QSS dark theme and future assets.
- `data/` — Parquet-first storage (`raw`, `interim`, `processed`, `external`); processed data includes players, teams, coaches, and games.
- `scripts/` — operational scripts (bootstrap placeholder included).
- `tests/` — reserved for unit/integration tests.

## Data workflow

1) Pull/generate base datasets via NFLreadpy or the synthetic generator (`scripts/generate_fake_nfl_data.py`) — players, teams, coaches, and games (regular season + postseason rounds). The UI ticker reads from `games.parquet`.
2) (Planned) Augment with Pro-Football-Reference scraping where NFLreadpy lacks coverage.
3) Normalize and persist Parquet tables to `data/processed`.
4) UI reads Parquet via `gridironlabs.data.repository.ParquetSummaryRepository` to populate summary pages, search, and schedule-aware views.

## Next steps you can tackle

- Flesh out PFR scraping targets and caching.
- Define final Parquet schemas for players/teams/coaches and add validation.
- Ensure `ParquetSummaryRepository` stays aligned with Parquet schemas and handles partial/missing slices gracefully.
- Implement Home dashboard content (leaders, standings, news ticker, etc.).
- Build UI tabs for players, teams, coaches, drafts, and comparisons.
- Add tests (pytest/pytest-qt) for services and widget smoke coverage.
