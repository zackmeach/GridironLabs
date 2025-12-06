 # services/
 
 Application-level services that mediate between UI and data.
 
 - `search_service.py` performs in-memory search across summaries.
 - `summary_service.py` surfaces single-entity summaries for UI panels.
 
 Swap service implementations freely so long as they honor the repository interface.

During bootstrap, services are wired with an in-memory repository so the UI can launch without external dependencies; swap in Parquet-backed repositories as data flows arrive.
