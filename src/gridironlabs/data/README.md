# data

- `schemas.py` — versioned Parquet schema definitions for entities.
- `repository.py` — SummaryRepository protocol and Parquet-backed implementation used by services/UI. Normalizes text/number/date fields, parses ratings/stats maps, caches loaded tables in memory, and surfaces schema/IO issues via typed errors.
- `sources/` — adapters for nflreadpy and Pro-Football-Reference.

Data IO must remain Parquet-first, tracked under `data/processed` with provenance.
