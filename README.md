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
- You should see a dark-themed shell with a persistent top nav (cycling upcoming matchups from `games.parquet`), a 2x-height context bar with stat chips, and stacked pages.
  - Home includes **League Standings**, **League Leaders**, and a full-height **League Schedule** panel (clickable stat headers re-rank leaders best-to-worst; schedule groups by week/day).
  - League Leaders includes an OOTP-style filter row (conference/division/team; age/rookie is scaffolded).
  - Settings now includes a basic settings-form surface (TabStrip + FormGrid) as a reference archetype.
  - A dev-only **Table Demo** page exists in the stack (`page-table-demo`) to validate the `OOTPTableView` + sorting + persistence at 1k+ rows.
- If `data/processed` is empty or Parquet fails validation, the app still boots and the context bar will reflect a zero-count/validation status; the matchup ticker may have no items. Seed Parquet with `python scripts/generate_fake_nfl_data.py` if you want matchups to cycle in the top nav.
- Run smoke tests (includes pytest-qt UI check): `pytest`

## UI snapshot tool (agent workflow)

Capture deterministic PNG + JSON snapshots of any page or panel by `objectName` (stable IDs defined in the UI code):

```bash
python scripts/ui_snapshot.py --page page-home --panel panel-league-leaders --name home-leaders
```

Outputs land in `ui_artifacts/` by default:

- `<name>.window.png` — full window render
- `<name>.target.png` — cropped page/panel render
- `<name>.json` — widget tree + geometry + scroll diagnostics for the target subtree

Use `--list-pages` to discover page objectNames and `--list-panels --page <page_objectName>` for panel IDs. Override output directory with `--out <path>`.

## Architecture

- `src/gridironlabs/core` — configuration, domain models, repository interfaces, logging wiring. Environment variables are loaded from `.env` when present and directories are created on boot.
- `src/gridironlabs/data` — Parquet IO helpers plus source adapters for NFLreadpy and PFR scraping; schemas now include games (schedules + outcomes). The default repository normalizes stats/ratings, caches tables in memory, and will surface schema/IO issues via typed errors.
- `src/gridironlabs/services` — UI-facing services (search, summary retrieval).
- `src/gridironlabs/ui` — PySide6 windows/widgets; persistent top navigation bar (with rotating matchup ticker), a 2x-height context bar with the page title/subtitle/stats, and stacked pages. Page titles render only in the context bar. Navigation history (back/forward), settings, and search hooks are wired up; seasons/teams/players/drafts/history pages are scaffolded while team/player summaries render when triggered from Home. The Home dashboard demonstrates dense table/list surfaces (standings + leaders) with OOTP-style “locked surface” scrolling via `make_locked_scroll(...)`. Large-table surfaces are intended to use `OOTPTableView` (QTableView + proxy sorting) with QSettings-backed persistence.
- `src/gridironlabs/resources` — QSS dark theme and future assets.
- `data/` — Parquet-first storage (`raw`, `interim`, `processed`, `external`); processed data includes players, teams, coaches, and games.
- `scripts/` — operational scripts (bootstrap placeholder included).
- `tests/` — reserved for unit/integration tests.

## Data workflow

1) Pull/generate base datasets via NFLreadpy or the synthetic generator (`scripts/generate_fake_nfl_data.py`) — players, teams, coaches, and games (regular season + postseason rounds). The UI ticker reads from `games.parquet`.
2) (Planned) Augment with Pro-Football-Reference scraping where NFLreadpy lacks coverage.
3) Normalize and persist Parquet tables to `data/processed`.
4) UI reads Parquet via `gridironlabs.data.repository.ParquetSummaryRepository` to populate the shell (context stats, matchup ticker) and future pages/panels.

## Next steps you can tackle

- Flesh out PFR scraping targets and caching.
- Define final Parquet schemas for players/teams/coaches and add validation.
- Ensure `ParquetSummaryRepository` stays aligned with Parquet schemas and handles partial/missing slices gracefully.
- Scale the panel system across the remaining pages (Teams/Players/etc.) using the Home standings panel as the canonical table/list archetype.
- Build UI tabs for players, teams, coaches, drafts, and comparisons.
- Add tests (pytest/pytest-qt) for services and widget smoke coverage.
