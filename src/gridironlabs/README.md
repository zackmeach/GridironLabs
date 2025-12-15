# gridironlabs package

Application code organized by responsibility:

- `core` — config, paths, logging, shared domain models.
- `data` — schemas, repositories, and source adapters (nflreadpy, PFR).
- `services` — search, summary fetchers feeding the UI.
- `ui` — PySide6 windows and widgets, including the reusable Page → GridCanvas → PanelCard framework (see `ui/pages/settings_page.py` for an example).
- `resources` — QSS theme and future assets packaged with the app.
