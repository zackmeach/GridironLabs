# Snapshot utility jump-off (agent notes)

Goal: deterministic CLI snapshots (PNG + JSON) for specific pages/panels by Qt `objectName`.

## How to run

```bash
python scripts/ui_snapshot.py --page page-home --panel panel-league-leaders --name home-leaders
```

Key flags:

- `--page <page_objectName>` (required for page/panel snapshot)
- `--panel <panel_objectName>` (optional crop target; defaults to the page)
- `--out <dir>` (default `ui_artifacts/`)
- `--name <label>` (stable filenames)
- Discovery helpers: `--list-pages`, `--list-panels --page <page_objectName>`, `--panel-only <panel_objectName>`

Outputs land in `ui_artifacts/`:

- `<name>.png` – full window render
- `<name>.target.png` – cropped page/panel render
- `<name>.json` – widget tree + geometry, scroll diagnostics, env/font/screen metadata

## Implementation decisions

- Helper module: `src/gridironlabs/ui/dev/snapshot.py` handles geometry settling, DPI-correct crops, widget tree capture (`capture_widget_tree`), and scroll diagnostics.
- CLI: `scripts/ui_snapshot.py` boots the real shell, loads the QSS theme, and navigates via `GridironLabsMainWindow.navigate_to(...)` using page/panel objectNames.
- Stable targeting: set `objectName` on pages/panels (e.g., `page-home`, `panel-league-schedule`) so snapshots stay deterministic.

## Files touched

- `scripts/ui_snapshot.py`
- `src/gridironlabs/ui/dev/snapshot.py`
- `src/gridironlabs/ui/main_window.py`
- Docs: `README.md`, `docs/README.md`, `docs/ui_panels.md`
