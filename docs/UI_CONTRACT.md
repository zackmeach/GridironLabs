# UI Contract (OOTP-style Panel System)

This document is the **source-of-truth contract** for how GridironLabs UI is composed and how UI state is persisted. It exists to prevent “UI drift” as new pages/panels are added.

## Panel composition contract

- **Pages** are composed as: **Page → GridCanvas → PanelChrome**.
- **PanelChrome** is the canonical container placed on the grid. It is an OOTP-style vertical stack:
  - Primary header (title + actions)
  - Secondary header (filters / paging / quick controls)
  - Tertiary header (column semantics / sort row)
  - Body (content)
  - Footer (meta + optional controls)

### Public API guardrail

Use `PanelChrome` convenience methods rather than reaching into bar internals:
- Primary: `add_action_left/right(...)`, `set_primary_left/right(...)`, `clear_actions()`
- Secondary: `set_filters_left/right(...)`, `clear_filters()`
- Tertiary: `set_columns_left/right(...)`, `clear_columns()`
- Footer: `set_footer(...)` / `set_footer_text(...)`

Avoid using:
- `show_secondary_header(...)`, `show_tertiary_header(...)` (deprecated escape hatches)
- `panel.advanced.*` (escape hatch for rare edge cases)

### Styling contract (QSS-first)

- **Do not** call `setStyleSheet(...)` inside reusable widgets/panels.
- Prefer stable `objectName` anchors + dynamic properties.

Key properties/selectors:
- `QFrame#PanelChrome[panelVariant="..."]` (variant styling lives in QSS)
- `QAbstractScrollArea[scrollVariant="hidden"]` (opt-in hidden scrollbars)

`panelVariant` semantics:
- **card**: padded “card content” panels (forms, summary blocks)
- **table**: dense table-like surfaces (standings/leaderboards/lists)

Note: **layout padding** for the panel body is applied in code (layout margins). QSS is used for the *visual* contract (colors, borders, typography).

## Persistence conventions (QSettings)

### Naming

Prefer stable IDs:
- **`page_id`**: match the page `objectName` (e.g. `page-players`, `page-table-demo`)
- **`table_id`**: stable dot-notation (e.g. `players.list`, `teams.roster`, `games.log`)
- **`version`**: string like `v1`, `v2`, …

### When to bump `version`

Bump when the **meaning/shape** of persisted state changes:
- column schema changes (add/remove/reorder semantic columns)
- changing which columns are persisted (e.g., stop stretching last section)
- sort semantics changes (e.g., sort role changes meaning)

Do **not** bump for:
- label text changes
- minor theme/spacing changes

### Key layout

Tables should persist under:

`ui/pages/<page_id>/tables/<table_id>/<version>/...`

Current convention in code:
- widths: `.../columns/widths` (comma-separated)
- sort: `.../sort/column`, `.../sort/order`

## Delegate color policy (prevent drift)

### Policy choice

Delegates may need to paint colors that QSS cannot control directly. When that happens:

- Use a **Python token policy**: paint-time colors must come from centralized tokens (not ad-hoc literals).
- Tokens should mirror the semantic tiers used by the theme (so the UI reads consistently).

### Ratings tiers (OVR/POT etc.)

Rating tier thresholds are intentionally coarse and stable:
- **elite**: ≥ 70
- **good**: ≥ 55
- **avg**: ≥ 40
- **poor**: < 40

Tier colors should match the theme’s semantic palette (see `src/gridironlabs/ui/style/tokens.py`).

## Glossary (agent quick reference)

- **`objectName`**: Qt widget identifier used heavily by QSS selectors (e.g., `QFrame#PanelChrome`).
- **QSS-first**: styling belongs in `src/gridironlabs/resources/theme.qss`, not in per-widget `setStyleSheet(...)`.
- **`PanelChrome`**: canonical panel container used on the grid; owns header bars + body + optional footer.
- **`panelVariant`**: dynamic property on `PanelChrome` used to distinguish **card** vs **table** panels (QSS may style by it; code sets body padding defaults).
- **Primary/Secondary/Tertiary header bars**:
  - **Primary**: title + actions (panel-level).
  - **Secondary**: filters/paging/quick controls.
  - **Tertiary**: column semantics / sort header row for table-like panels.
- **Content-driven visibility**: bars show/hide based on whether they contain content (avoid manual `show_*` toggles).
- **`scrollVariant`**: dynamic property on `QAbstractScrollArea` to opt into “hidden scrollbars” styling (e.g., `scrollVariant="hidden"`).
- **Locked surface**: a dense list/table surface where scrolling should only appear if overflow is real (not off-by-1px rounding).
- **`MicroScrollGuard`**: helper that suppresses accidental ~1px scroll ranges on locked surfaces.
- **`make_locked_scroll(...)`**: helper that wires `scrollVariant="hidden"` + scroll policies + `MicroScrollGuard` for a given content widget.
- **`ColumnSpec`**: shared column definition (key/label/width/alignment) used to keep header and rows aligned (prevents “drift”).
- **`OOTPTableView`**: QTableView wrapper for high-row-count tables (sorting, consistent row height, persistence hooks).
- **Persistence keys**:
  - **`page_id`**: stable page identifier (prefer the page `objectName`).
  - **`table_id`**: stable table identifier (prefer dot-notation like `players.list`).
  - **`version`**: persistence schema version; bump when persisted meaning/shape changes.
