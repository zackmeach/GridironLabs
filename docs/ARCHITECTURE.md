# Architecture

Gridiron Labs follows a layered desktop architecture built for offline-friendly analytics.

## Layers

- **Core**: AppConfig/AppPaths, structured logging, shared domain models.
- **Data**: Versioned Parquet schemas (players, teams, coaches, games), repository adapters for nflreadpy + PFR.
- **Services**: Search and summary orchestration, ready for ranking/enrichment.
- **UI**: PySide6 shell (nav + context bar + content stack). Page titles live only in the context bar. Pages are built with the Page → GridCanvas → PanelCard framework. Interactive entity navigation (clicking teams/players) is supported via specialized summary pages. The nav bar also exposes search + settings affordances and back/forward history controls.
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

## Runtime bootstrap

1. Resolve paths via `AppPaths.from_env` and load `.env` overrides (directories are created if missing).
2. Build `AppConfig` (feature flags: scraping, live refresh, schema version, UI theme).
3. Configure structured logging (console + rotating file via `JsonFormatter`).
4. Initialize the Parquet repository + services (search, summary), caching entities in memory and normalizing text/numeric/date fields.
5. Start PySide6 shell with navigation, a context bar under the nav (2x nav height), and stacked pages. Home bootstraps standings/leaders from the repository, season span text from era fields, and an upcoming-matchup ticker from `games.parquet`. Page titles are not repeated in body content; pages render content via panel cards placed on a grid canvas.
6. Navigation history is tracked for browser-style back/forward controls. Search submissions build an in-memory index the first time a query is run and route users to the search page scaffold.

## Quality & testing guardrails

- Ruff + mypy (disallow untyped public defs) enabled by default.
- Pytest layout for unit, integration (Parquet + HTTP mocking), and pytest-qt smoke.
- Performance targets: <2s startup, <150ms search on processed data.
