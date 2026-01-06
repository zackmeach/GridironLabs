# Panel system verification gate

This document is a **self-contained verification gate** for the PanelChrome framework.
It lists key invariants and where to verify them (code + tests).

Status values:
- **Fixed**: implemented in the codebase (with references).
- **Not needed**: obsolete or conflicts with chosen direction.
- **Deferred**: valid, intentionally postponed (with a follow-up target).

---

## A) Immediate correctness / drift risks

### A1) Missing `Callable` import

- **Status**: **Fixed**
- **Evidence**: `Callable` is imported and used in `HomePage`:
  - `src/gridironlabs/ui/main_window.py`

### A2) Inline `setStyleSheet(...)` on header labels

- **Status**: **Fixed**
- **Evidence**: Header label styling is in QSS:
  - `src/gridironlabs/resources/theme.qss`
- **Notes**: Keep this invariant going forward: **no per-widget inline QSS** for reusable panel archetypes.

### A3) Docs vs implementation mismatch: PanelChrome “body API”

- **Status**: **Fixed**
- **Evidence**:
  - `PanelChrome` implements `set_body`, `add_body`, `clear_body`, `set_body_padding` in `src/gridironlabs/ui/panels/panel_chrome.py`
  - Panel docs updated in `docs/ui_panels.md`

### A4) Secondary/Tertiary headers hidden despite having content

- **Status**: **Fixed**
- **Evidence**:
  - `HomePage` uses content-driven bar composition via `PanelChrome.set_filters_left(...)` and `PanelChrome.set_columns_left(...)`:
    - `src/gridironlabs/ui/main_window.py`
  - Bar visibility is content-driven (`PanelBar.update_visibility()` is called after slot updates; `PanelBar.clear()` hides when empty):
    - `src/gridironlabs/ui/panels/bars/standard_bars.py`

---

## B) Standings table surface (canonical “table-ish panel archetype”)

### B1) Add a real body

- **Status**: **Fixed**
- **Evidence**: `LeagueStandingsWidget` exists and is set as body via `PanelChrome.set_body(...)`:
  - `src/gridironlabs/ui/widgets/standings.py`
  - `src/gridironlabs/ui/main_window.py`

### B2) Header/row horizontal alignment double-inset risk

- **Status**: **Fixed**
- **Evidence**:
  - `TertiaryHeaderBar` has QSS padding `0px 8px` in `src/gridironlabs/resources/theme.qss`
  - `StandingsHeaderRow` margins are now `(0, 0, 0, 0)` so the bar’s padding is the single inset source:
    - `src/gridironlabs/ui/widgets/standings.py`

### B3) Row click -> navigation (team page)

- **Status**: **Fixed**
- **Evidence**:
  - `StandingsRow` accepts `on_click` and forwards `team_name` on left-click:
    - `src/gridironlabs/ui/widgets/standings.py`
  - `HomePage` passes `on_team_click` into `LeagueStandingsWidget`:
    - `src/gridironlabs/ui/main_window.py`

### B4) ColumnSpec extraction

- **Status**: **Fixed**
- **Evidence**:
  - `STANDINGS_COLUMNS` is the shared ColumnSpec list used by both header and row rendering:
    - `src/gridironlabs/ui/widgets/standings.py`

### B5) Logo loading: caching + correct pathing

- **Status**: **Fixed**
- **Evidence**:
  - Centralized logo provider and cache:
    - `src/gridironlabs/ui/assets/logos.py`
  - Standings uses the provider:
    - `src/gridironlabs/ui/widgets/standings.py`

---

## C) Panel framework hardening

### C1) Implement `PanelBar.clear()`

- **Status**: **Fixed**
- **Evidence**: `PanelBar.clear()` is implemented and updates visibility in `src/gridironlabs/ui/panels/bars/standard_bars.py`

### C2) Header auto-visibility rules

- **Status**: **Fixed**
- **Evidence**:
  - Adding content shows the bar (`add_left/add_right`)
  - Clearing content hides the bar when empty (`clear()` + `update_visibility()`)
  - Primary bar keeps its special rule (`PrimaryHeaderBar.update_visibility()`)
  - `src/gridironlabs/ui/panels/bars/standard_bars.py`

### C3) Table vs card panel variant ergonomics

- **Status**: **Fixed**
- **Evidence**:
  - `PanelChrome(..., panel_variant="table")` defaults body padding to 0:
    - `src/gridironlabs/ui/panels/panel_chrome.py`
  - Home page standings uses the table variant:
    - `src/gridironlabs/ui/main_window.py`

---

## D) Theme / scrolling behavior

### D1) Global hidden scrollbars

- **Status**: **Fixed**
- **Evidence**:
  - Scrollbar hiding is now scoped to `scrollVariant="hidden"` in `src/gridironlabs/resources/theme.qss`
  - Standings sets the property on its scroll area:
    - `src/gridironlabs/ui/widgets/standings.py`

---

## E) Manual verification checklist (post-change)

After implementing P0/P1 items, verify manually:

1. **Alignment**
   - Tertiary header column labels start at the same x-position as row data.
2. **Interactivity**
   - Standings rows show pointing-hand cursor.
   - Clicking a row navigates to the Team Summary page (or at minimum triggers the callback).
3. **Scroll**
   - Standings scroll works with mouse wheel/trackpad/keys.
   - Scrollbars are hidden only on widgets with `scrollVariant="hidden"`.
4. **No drift**
   - No new `setStyleSheet(...)` calls added for panel archetype widgets.
