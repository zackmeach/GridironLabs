# Architecture

Gridiron Labs follows a layered desktop architecture built for offline-friendly analytics.

## Layers

- **Core**: AppConfig/AppPaths, structured logging, shared domain models.
- **Data**: Versioned Parquet schemas (players, teams, coaches, games), repository adapters for nflreadpy + PFR.
- **Services**: Search and summary orchestration, ready for ranking/enrichment.
- **UI**: PySide6 shell (nav + context bar + content stack). Page titles live only in the context bar. Pages are built with the Page → GridCanvas → PanelChrome framework (PanelChrome is currently a minimal panel box; richer chrome comes later). Interactive entity navigation (clicking teams/players) is supported via specialized summary pages. The nav bar also exposes search + settings affordances and back/forward history controls.
- **Scripts**: Operational entrypoints for refresh and synthetic data.

## Data flow (current scaffold)

```text
Sources (nflreadpy, PFR scraping)
      │
      ▼
Data scripts (refresh) ──► data/raw & data/interim
      │
      ▼
Normalization/validation ──► Parquet schemas ──► data/processed
      │
      ▼
ParquetSummaryRepository (players/teams/coaches/games) ──► Services (summary, search) ──► UI views
```

Note: `scripts/refresh_data.py` is currently a **partial refresh** focused on downloading team logos and enriching `data/processed/teams.parquet` with `logo_path` / `logo_url`. Full end-to-end ingestion (fetch/merge/validate/write for all tables) is still scaffolded.

## Runtime bootstrap

1. Resolve paths via `AppPaths.from_env` and load `.env` overrides (directories are created if missing).
2. Build `AppConfig` (feature flags: scraping, live refresh, schema version, UI theme).
3. Configure structured logging (console + rotating file via `JsonFormatter`).
4. Initialize the Parquet repository + services (search, summary), caching entities in memory and normalizing text/numeric/date fields.
5. Start PySide6 shell with navigation, a context bar under the nav (2x nav height), and stacked pages. The shell bootstraps context stats (players/teams/coaches/seasons span) and an upcoming-matchup ticker from `games.parquet`. Page titles are not repeated in body content; pages render body content via `PanelChrome` instances placed on a grid canvas (PanelChrome is currently a minimal box with a `body_layout`).
6. Navigation history is tracked for browser-style back/forward controls. Search submissions build an in-memory index the first time a query is run and route users to the search page scaffold.

## Quality & testing guardrails

- Ruff + mypy (disallow untyped public defs) enabled by default.
- Pytest layout for unit, integration (Parquet + HTTP mocking), and pytest-qt smoke.
- Performance targets: <2s startup, <150ms search on processed data.
