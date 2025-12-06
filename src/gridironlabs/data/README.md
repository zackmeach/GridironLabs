# data

- `schemas.py` — versioned Parquet schema definitions for entities.
- `repository.py` — SummaryRepository protocol and Parquet stub.
- `sources/` — adapters for nflreadpy and Pro-Football-Reference.

Data IO must remain Parquet-first, tracked under `data/processed` with provenance.
