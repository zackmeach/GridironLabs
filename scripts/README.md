 # scripts/
 
 Operational scripts for data ingestion and maintenance.
 
 - `bootstrap_data.py` (placeholder) – orchestrate pulls from NFLreadpy and PFR scraper, then write Parquet into `data/processed`.
 
 Keep scripts idempotent and fast; heavy scraping should cache results locally.
