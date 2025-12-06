# data

Parquet-first storage layout:

- `raw/` — unprocessed pulls from sources (nflreadpy, PFR).
- `interim/` — in-progress normalization/caching.
- `processed/` — canonical, schema-validated tables consumed by the UI.
- `external/` — third-party reference data.

Keep provenance (source, timestamp, schema version) alongside each dataset.
