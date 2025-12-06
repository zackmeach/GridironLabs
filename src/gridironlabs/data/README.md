 # data/
 
 Data ingestion and persistence utilities.
 
 - `loaders/` wraps local Parquet IO, ensuring directories exist.
 - `sources/` contains external clients:
   - `nflreadpy_client.py` – pulls base data via NFLreadpy.
   - `pfr_scraper.py` – placeholder scraper for Pro-Football-Reference.
 
 Expected flow:
 1) Fetch from NFLreadpy and PFR scraper.
 2) Normalize and write Parquet into `data/processed`.
 3) UI and services read Parquet via `loaders/`.

Paths default to `data/` at the repo root; override with `GRIDIRONLABS_DATA_ROOT` in `.env` if needed.
