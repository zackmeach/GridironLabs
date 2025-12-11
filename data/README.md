# data

Parquet-first storage layout:

- `raw/` — unprocessed pulls from sources (nflreadpy, PFR).
- `interim/` — in-progress normalization/caching.
- `processed/` — canonical, schema-validated tables consumed by the UI.
- `external/` — third-party reference data.

Keep provenance (source, timestamp, schema version) alongside each dataset.

Notes:
- If `data/processed` is empty, the app will start with an offline/banner warning and placeholder views.
- Use `python scripts/generate_fake_nfl_data.py` to quickly seed players/teams/coaches/games Parquet for local UI testing.