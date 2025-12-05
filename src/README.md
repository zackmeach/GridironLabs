 # Source Layout
 
 The Python package lives under `gridironlabs` and is organized for clear UI/data separation:
 
 - `core/` – configuration, domain models, repository interfaces.
 - `data/` – ingestion helpers (Parquet IO, scraping, external API clients).
 - `services/` – application services (search, summaries) that bridge UI and data.
 - `ui/` – PySide6 widgets, windows, and styling.
 - `resources/` – static assets like QSS themes.
 - `app.py` / `main.py` – bootstrap and CLI entry point.
