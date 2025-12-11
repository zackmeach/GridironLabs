# gridironlabs package

Application code organized by responsibility:

- `core` — config, paths, logging, shared domain models.
- `data` — schemas, repositories, and source adapters (nflreadpy, PFR).
- `services` — search, summary fetchers feeding the UI.
- `ui` — PySide6 windows, widgets, reusable state panels (including the League Leaders home grid and a static Settings page matching the latest mock).
- `resources` — QSS theme and future assets packaged with the app.
