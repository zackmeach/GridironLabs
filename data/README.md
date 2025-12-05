 # data directory
 
 Local, versioned storage for structured datasets (Parquet-first).
 
 - `raw/` – direct outputs from source systems or scrapers.
 - `interim/` – temporary cleaned/normalized tables.
 - `processed/` – final curated datasets used by the app UI.
 - `external/` – third-party or manually provided data drops.
 
 Large Parquet files can be git-ignored; document any manual steps to regenerate them.
