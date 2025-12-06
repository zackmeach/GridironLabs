 # GridironLabs Package
 
 This package hosts the PySide6 desktop app plus data orchestration layers.
 
- `core/` defines configuration, domain models, repository interfaces, and logging setup.
 - `data/` wraps external sources (NFLreadpy, PFR scraping) and local Parquet IO.
 - `services/` contains UI-facing application services (search, summaries).
- `ui/` is the OOTP26-inspired shell, reusable widgets, and placeholder states.
 - `resources/` stores styles and assets used by the UI.
 
The entry point `main.py` wires dependencies, applies the stylesheet, and starts the UI via `app.run()`.
