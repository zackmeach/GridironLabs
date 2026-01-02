# ui

PySide6 desktop shell pieces:

- `app.py` — application bootstrapper for the desktop runtime.
- `main_window.py` — maximized window with persistent top nav (includes rotating upcoming-week matchup ticker pulled from `games.parquet`), a context bar under the nav (2x nav height) that holds the page title/subtitle/stats (titles are not repeated in the body), and stacked pages. Navigation history (back/forward), search submission handling, and settings entrypoints are wired here.
- `pages/` — page implementations (many are placeholders/scaffolds).
- `layouts/` — layout helpers (e.g. `GridCanvas`).
- `overlays/` — overlay widgets (e.g. debug grid overlay).
- `style/` — Python-side tokens used by widgets/layout defaults.
- `panels/` — OOTP-style panel chrome primitives. `PanelChrome` provides optional header bars (primary/secondary/tertiary), a body region (managed via `set_body` / `add_body`), and an optional footer. Bar widgets live in `panels/bars/`.
- `assets/` — UI asset helpers (e.g. cached logo pixmaps loaded from `data/external/logos/`).
- `widgets/` — reusable widgets (navigation bar, standings/leaders bodies, filters, key/value lists, rating bars, rich text, charts, scoreboard, tab strip, form grid).
- `table/` — model/view table foundation (`OOTPTableView`, shared `ColumnSpec`, base models, delegates).
- `persistence/` — QSettings helpers for UI persistence (tables first).
- `resources` (../resources) — dark theme QSS and future assets.

Settings page note:
- Settings now includes a basic settings-form reference surface (TabStrip + FormGrid) implemented as a `PanelChrome` card.

Running the UI locally:
- Ensure the venv is active (`source .venv/bin/activate` or `.\\.venv\\Scripts\\activate` on Windows).
- Dependencies: `pip install -e .[dev]`; on Windows you may need `pip install pyside6 polars` if not already present.
- If `data/processed` is empty or validation fails, the app still boots; context stats will reflect zero/validation status and the matchup ticker may have no items. Seed Parquet with `python scripts/generate_fake_nfl_data.py` if you want matchups to cycle in the top nav and summary pages to populate.
- Home dashboard note:
  - The **League Leaders** panel includes an OOTP-style filter row (conference/division/team) powered by a static mapping. Age/rookie is scaffolded but disabled until player metadata is available.

Scrolling note:
- The theme supports OOTP-style hidden scrollbars **per-surface** via `scrollVariant="hidden"` on `QAbstractScrollArea` (default platform scrollbars remain enabled for future large-table pages).
  - For dense “locked surface” panels, use `make_locked_scroll(...)` (`src/gridironlabs/ui/widgets/scroll_guard.py`) to apply consistent scroll config + `MicroScrollGuard` suppression of accidental 1px micro-scroll.

Table demo note:
- `TableDemoPage` (`page-table-demo`) exists in the stacked pages as a dev-only proof surface for `OOTPTableView` (1k+ rows, sorting, and QSettings persistence).
