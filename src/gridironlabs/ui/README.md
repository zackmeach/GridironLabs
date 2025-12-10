# ui

PySide6 desktop shell pieces:

- `app.py` — application bootstrapper for the desktop runtime.
- `main_window.py` — maximized window with persistent top nav (includes rotating upcoming-week matchup ticker pulled from `games.parquet`), a page context bar under the nav, and stacked pages. Home renders a League Leaders grid fed by Parquet stats.
- `widgets/` — reusable navigation bar (with history/search/settings), page context bar styles, state banners, and the `league_leaders.py` panel.
- `resources` (../resources) — dark theme QSS and future assets (styles include the leaders grid).
