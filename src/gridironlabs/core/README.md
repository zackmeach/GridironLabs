 # core/
 
 Domain primitives and configuration shared across the app.
 
 - `config.py` centralizes filesystem paths, feature flags, and configuration factory.
- `logging_utils.py` configures structured console + rotating file logging.
 - `models.py` defines summary dataclasses for players, teams, and coaches.
 - `repository.py` declares repository interfaces consumed by services and UI.

Environment overrides:
- `.env` (optional) plus `GRIDIRONLABS_*` variables can point `data_root`, toggle `enable_scraping` / `enable_live_refresh`, and force offline mode.
