 # GridironLabs Package
 
 This package hosts the PySide6 desktop app plus data orchestration layers.
 
 - `core/` defines configuration, domain models, and repository interfaces.
 - `data/` wraps external sources (NFLreadpy, PFR scraping) and local Parquet IO.
 - `services/` contains UI-facing application services (search, summaries).
 - `ui/` is the OOTP26-inspired shell and reusable widgets.
 - `resources/` stores styles and assets used by the UI.
 
 The entry point `main.py` wires dependencies and starts the UI via `app.run()`.
