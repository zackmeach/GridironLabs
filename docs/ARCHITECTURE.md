# Architecture

Gridiron Labs follows a layered desktop architecture built for offline-friendly analytics.

## Layers
- **Core**: AppConfig/AppPaths, structured logging, shared domain models.
- **Data**: Versioned Parquet schemas, repository adapters for nflreadpy + PFR.
- **Services**: Search and summary orchestration, ready for ranking/enrichment.
- **UI**: PySide6 shell (nav + content stack) with reusable state panels.
- **Scripts**: Operational entrypoints for refresh and synthetic data.

## Data flow (current scaffold)
```
Sources (nflreadpy, PFR scraping)
      │
      ▼
Data scripts (refresh) ──► data/raw & data/interim
      │
      ▼
Normalization/validation ──► Parquet schemas ──► data/processed
      │
      ▼
ParquetSummaryRepository ──► Services (summary, search) ──► UI views
```

## Runtime bootstrap
1. Resolve paths via `AppPaths.from_env` and load `.env` overrides.
2. Build `AppConfig` (feature flags: scraping, live refresh).
3. Configure structured logging (console + rotating file).
4. Initialize repository + services (search, summary).
5. Start PySide6 shell with navigation and placeholder content.

## Quality & testing guardrails
- Ruff + mypy (disallow untyped public defs) enabled by default.
- Pytest layout for unit, integration (Parquet + HTTP mocking), and pytest-qt smoke.
- Performance targets: <2s startup, <150ms search on processed data.
