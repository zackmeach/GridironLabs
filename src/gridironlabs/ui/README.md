# ui

PySide6 desktop shell pieces:

- `app.py` — application bootstrapper for the desktop runtime.
- `main_window.py` — maximized window with persistent top nav (includes rotating upcoming-week matchup ticker pulled from `games.parquet`), a context bar under the nav (2x nav height) that holds the page title/subtitle/stats (titles are not repeated in the body), and stacked pages.
- `pages/` — page implementations. `settings_page.py` is the reference implementation for the Page → GridCanvas → PanelCard framework.
- `layouts/` — layout helpers (e.g. `GridCanvas`).
- `overlays/` — overlay widgets (e.g. debug grid overlay).
- `style/` — Python-side tokens used by widgets/layout defaults.
- `widgets/` — reusable widgets (navigation bar, panel cards, state banners, optional panels like `league_leaders.py`).
- `resources` (../resources) — dark theme QSS and future assets.

Settings page note:
- Settings is the example page demonstrating panel placement and the configurable debug grid overlay.

Running the UI locally:
- Ensure the venv is active (`source .venv/bin/activate` or `.\\.venv\\Scripts\\activate` on Windows).
- Dependencies: `pip install -e .[dev]`; on Windows you may need `pip install pyside6 polars` if not already present.
- If `data/processed` is empty, the app still boots; context stats will be zero and the matchup ticker may have no items. Seed Parquet with `python scripts/generate_fake_nfl_data.py` if you want matchups to cycle in the top nav.
