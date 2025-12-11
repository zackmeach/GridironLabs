# ui

PySide6 desktop shell pieces:

- `app.py` — application bootstrapper for the desktop runtime.
- `main_window.py` — maximized window with persistent top nav (includes rotating upcoming-week matchup ticker pulled from `games.parquet`), a context bar under the nav (2x nav height) that holds the page title/subtitle/stats (titles are not repeated in the body), and stacked pages. Home renders a League Leaders grid fed by Parquet stats. The Settings page is a cosmetic mock matching the shared reference: four panels with a 4/3/3 width split (Data Generation, UI Grid Layout + Test Cases stacked, Debug Output) and aligned heights.
- `widgets/` — reusable navigation bar (with history/search/settings), page context bar styles, state banners, and the `league_leaders.py` panel.
- `resources` (../resources) — dark theme QSS and future assets (styles include the leaders grid).

Settings mock details:
- Panels: Data Generation (season range combos, toggles, grouped checkboxes, last-update table, full-width Generate button), UI Grid Layout (toggle, opacity slider, color swatch + hex input, cell size spinbox), Test Cases (three toggles + Execute button), Debug Output (terminal-like readout).
- Layout ratios: Data Generation 4/10, middle column (UI Grid Layout + gap + Test Cases) 3/10, Debug Output 3/10; vertical alignment keeps Data Generation and Debug Output equal height and matches the middle stack.
- All controls are cosmetic only; no signals are wired to behavior yet.
- Surface color: nav, context bar, and primary panels share the same background for visual unity.

Running the UI locally:
- Ensure the venv is active (`source .venv/bin/activate` or `.\\.venv\\Scripts\\activate` on Windows).
- Dependencies: `pip install -e .[dev]`; on Windows you may need `pip install pyside6 polars` if not already present.
- If `data/processed` is empty, the app will show an offline/banner warning; seed Parquet with `python scripts/generate_fake_nfl_data.py` for a richer home view.
