# ui

PySide6 desktop shell pieces:

- `app.py` — application bootstrapper for the desktop runtime.
- `main_window.py` — maximized window with persistent top nav and stacked pages. Home now renders a League Leaders grid fed by Parquet stats.
- `widgets/` — reusable navigation bar, state banners, and the new `league_leaders.py` panel.
- `resources` (../resources) — dark theme QSS and future assets (styles include the leaders grid).
