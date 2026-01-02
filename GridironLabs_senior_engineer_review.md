# GridironLabs — Senior Engineering Review (Panel System + OOTP26-style UI Framework)

_Date: 2026-01-01_

This review focuses on whether the current codebase is delivering the **core journey**, **goals**, and **design methodology** described in your project overview and docs, with a special focus on the **PanelChrome** framework and the two flagship implementations: **League Standings** and **League Leaders**.

---

## 1) The core journey, goals, and methodology (as documented)

### Core journey (user flow)
The intended “OOTP-like” experience is:

- A **persistent shell** (top navigation + context strip) that never “jumps.”
- Pages swap underneath, composed from a **grid** of dense, consistent panels.
- Each panel is built from the same contract: **PanelChrome** (header rows + body + footer).
- High-density surfaces (standings, leaders) should feel **locked** when content fits, and only scroll when overflow is real.
- Everything should be clickable: rows take you to deeper entity pages (team/player), without breaking UI rhythm.

### Primary goals
- **Robustness**: panel layout should be hard to “accidentally drift” as the app grows.
- **Consistency**: spacing, typography, header heights, row rhythm, and interactions should match across pages.
- **Malleability**: new panels should be fast to build without re-inventing chrome/layout rules.
- **Performance-friendly**: offline-first, fast navigation, data stored locally (Parquet) and loaded into UI surfaces quickly.

### Design methodology
- **Doc-driven UI contracts** (not ad-hoc widget composition).
- Styling is **QSS-first**; Python widgets cooperate via `objectName` and `property` selectors.
- A small number of “blessed primitives” (PanelChrome, GridCanvas, bar slots, ColumnSpec) are reused everywhere.
- Guardrails are enforced by **tests** and “verification gates,” not just conventions.

---

## 2) What’s implemented today (reality check)

### 2.1 Shell + navigation structure
**Status: solid foundation in place**

- `NavigationBar` implements a persistent top nav and context strip (`src/gridironlabs/ui/widgets/navigation.py`).
- `GridironLabsMainWindow` uses a page stack and history concepts (`src/gridironlabs/ui/main_window.py`).
- Context payloads (title/subtitle/stats) are structured and updated when data loads.

**What this means:** the app already “feels” like it’s being built as a *desktop workflow shell*, not a collection of screens.

### 2.2 Grid-based page composition
**Status: implemented and usable**

- `BasePage` owns a `GridCanvas` and exposes `add_panel(...)` (`src/gridironlabs/ui/pages/base_page.py`).
- `GridCanvas` is a 36-column `QGridLayout` wrapper with an optional debug overlay (`src/gridironlabs/ui/layouts/grid_canvas.py`).
- The Home page is currently used as a controlled sandbox for panel iteration.

**What this means:** you’re actually building the pages the way OOTP does: “cards/panels on a predictable grid.”

### 2.3 PanelChrome + bar system (the core UI primitive)
**Status: strong directionally, already useful, needs hardening**

- `PanelChrome` composes:
  - Primary header (title/actions)
  - Secondary header (filters/search/paging)
  - Tertiary header (column semantics/sort bar)
  - Body container (variant-dependent padding)
  - Footer (meta/actions)
- Bars are slot-based (`left_slot` + `right_slot`) with auto-visibility rules (`src/gridironlabs/ui/panels/bars/standard_bars.py`).
- Table panels can default to zero padding (`PanelChrome(..., panel_variant="table")`).

**What this means:** the project has the correct primitive. Most future UI can be expressed as “PanelChrome + body widget” without inventing new layouts.

### 2.4 League Standings + League Leaders implementations
**Status: impressive for an early milestone**

Home page (`src/gridironlabs/ui/main_window.py`) composes:

- **League Standings** panel:
  - `PanelChrome(title="LEAGUE STANDINGS", panel_variant="table")`
  - Uses tertiary header for column labels (`StandingsHeaderRow`)
  - Uses scrollable body (`LeagueStandingsWidget`) with:
    - section headers (`SectionBar`)
    - row widgets (`StandingsRow`)
    - logo loading + caching (`get_logo_pixmap`)
    - click-to-navigate behavior
- **League Leaders** panel:
  - `PanelChrome(title="LEAGUE LEADERS", panel_variant="table")`
  - Uses secondary header for `LeadersFilterBar`
  - Uses scrollable body (`LeagueLeadersWidget`) with category sections and sortable stat headers

**What this means:** your two flagship panels are already proving the panel framework is viable.

---

## 3) Vision-to-implementation scorecard

This isn’t “grade school scoring”—it’s a prioritization tool.

| Area | Alignment | Notes |
|---|---:|---|
| PanelChrome as canonical primitive | **High** | Correct structure, variants, slot-based bars, body container separation. |
| Avoiding UI drift | **Medium–High** | QSS-first + objectName/properties are strong; remaining risk is **API exposure** and **magic spacing** creeping in. |
| Table/list density & row rhythm | **High (so far)** | Standings and leaders are dense and readable; row height is consistent. |
| “Locked surface” scrolling | **High** | `scrollVariant="hidden"` + `MicroScrollGuard` directly targets OOTP feel. |
| Grid methodology (panel-on-grid) | **High** | 36-column placement with stable spans is working. |
| Extensibility to future surfaces | **Medium** | You’ll want a shared **ColumnSpec** / table surface helper and a path to model/view for large lists. |
| Testing guardrails | **Medium–High** | UI tests exist and validate invariants; coverage can expand as primitives stabilize. |
| Requirements/architecture cohesion | **Medium** | Docs are good; a few doc/code mismatches and TODOs remain (normal at this stage). |

---

## 4) Deep technical review (Panel system correctness + drift risk)

### 4.1 The biggest win: the structure is correct
You made the right “unsexy” decision early: **separate chrome from body** and enforce it everywhere.

- `PanelChrome` is a stable contract for all pages.
- Bars are composable and consistent.
- The theme is centralized (`src/gridironlabs/resources/theme.qss`).
- Widgets cooperate via `objectName`/`property` (great for long-term consistency).

This is exactly the foundation you want before scaling to dozens of panels.

### 4.2 The biggest remaining risk: “public mutability” of the contract
Right now, pages can reach into the panel and do things like:

```python
panel.header_tertiary.add_left(...)
panel.header_secondary.add_left(...)
```

That’s convenient (and fine during experimentation), but it’s also where drift is born over time:
- different pages will add different spacers/margins
- some will forget to show/hide headers consistently
- some will add “just one more” sub-layout and you’ll slowly lose the OOTP feel

**Recommendation (high leverage):** keep the widgets, but *narrow the API*.

Example direction:
- `panel.set_columns(widget)` (tertiary-left)
- `panel.set_filters(widget)` (secondary-left)
- `panel.add_action(widget)` (primary-right)
- `panel.set_footer(text=..., right_widget=...)`

Internally, `PanelChrome` routes to the correct bar slots and enforces invariants.

This is how you turn “a useful widget” into “a protected system.”

### 4.3 Header visibility rules should be contract-driven (not page-driven)
`PanelBar` already supports auto-visibility when slots have content. This is *great*.

But `PanelChrome` still relies on explicit calls like:
- `show_secondary_header(True/False)`
- `show_tertiary_header(True/False)`

That creates two sources of truth:
- “does the bar have content?” vs
- “did the page remember to show it?”

**Recommendation:** treat “show/hide” as an override, not the default workflow.

A clean approach:
- Bars default to `update_visibility()` rules.
- `PanelChrome` methods like `set_filters(...)` or `set_columns(...)` cause the right bar to become visible automatically.
- If you truly want to forcibly hide a bar (rare), you can expose `panel.disable_secondary_header()` as an explicit override.

### 4.4 The 1px scroll issue: your guard is good, but you should still instrument root cause
You already created `MicroScrollGuard` for “range=1px” overflows. That is a *very* OOTP-aware fix, and it’s implemented consistently.

But you’re correct to worry about “bandaging.”
The cause is usually one (or more) of these:
- border/padding rounding differences between `QScrollArea` viewport and content
- font metrics + fixed row height mismatch
- layout rounding at fractional DPI scaling
- grid pitch not being an exact multiple of row heights

**Recommendation:** keep the guard (it improves UX), but also add a tiny diagnostic mode.

Concrete approach:
- Add a debug log method that prints:
  - viewport height
  - content `sizeHint().height()`
  - scroll range
  - row count × row height (expected)
- Gate it behind a config flag (e.g., `GRID.debug_enabled`).

Then, when you hit the “last pixel cut” scenario, you’ll get immediate evidence of where the mismatch is.

### 4.5 GridCanvas row/column pitch vs “row rhythm”
`GridCanvas` is stretch-based (every row stretch = 1, every column stretch = 1). This is flexible, but it makes pixel-perfect “N rows exactly fit” tricky, because:
- available pixels are divided by `rows`
- Qt rounds (and borders/gaps eat pixels)
- a scroll area’s viewport will inherit any leftover

**Recommendation options (choose based on what you want long-term):**

**Option A (keep stretch grid, accept micro rounding):**
- Keep `MicroScrollGuard`
- Make sure all table surfaces tolerate 1–2px mismatches without visible drift
- This is the simplest and likely fine for most users.

**Option B (OOTP-style exact pitch for table surfaces):**
For “table panels,” consider a fixed vertical rhythm:
- Define `ROW_H` as a token (already done)
- Define `VISIBLE_ROWS` per panel region
- Compute a **body viewport height** = `VISIBLE_ROWS * ROW_H + section/header heights + borders`
- Set the panel or scroll viewport to a fixed height in pixels for those table surfaces

This sacrifices a bit of grid flexibility but produces the true “locked” OOTP feel.

### 4.6 ColumnSpec alignment: you started correctly—now generalize
The docs explicitly call out “use a shared ColumnSpec.” You did this for standings.

**Standings is the canonical archetype**: header row + rows share column widths and insets. That’s exactly what you want.

Next step is to extract the pattern into a reusable helper:
- `ColumnSpec` dataclass + “apply to header” + “apply to row”
- A lightweight `TableRowLayout` that handles:
  - left padding once (not twice)
  - consistent alignment flags
  - optional “logo column” behavior

Then leaders, team rosters, league stats tables, etc. can all use the same “table surface builder.”

### 4.7 Styling methodology: QSS-first is working
The theme file is already doing the heavy lifting.
You’ve mostly avoided the classic drift traps:
- no widget-specific `setStyleSheet(...)`
- consistent `objectName` usage
- `scrollVariant` property for global scroll behavior

**Two improvements to protect this:**
1) Keep token values (spacing/radius) mirrored between Python (`ui/style/tokens.py`) and QSS, but declare one as canonical. Right now it’s “QSS is canonical,” which is fine—just keep it explicit.
2) Reduce “magic numbers” in code for margins where possible; prefer a small token set so tweaks don’t fragment.

---

## 5) Panel-specific review

### 5.1 League Standings panel (flagship “table-ish” panel)
What’s working really well:
- Proper use of tertiary header for column semantics.
- Body padding = 0 for a dense table surface (good choice).
- `SectionBar` gives a clean division break without extra nested frames.
- `StandingsRow` click behavior is tested.
- Logo caching exists and is centralized.

What I’d tighten next:
- Ensure header and rows share **exactly one** horizontal inset (avoid double padding). If the QSS adds padding to the bar, then the header row widget should probably use 0 margins, and vice versa.
- Replace any “header height equals row height” coupling with a token-driven computation, so font changes don’t break row rhythm on different systems.

### 5.2 League Leaders panel (proof that the secondary header is real)
What’s working really well:
- Secondary header is being used exactly as intended (filters live in chrome, not body).
- Category sections establish a scalable pattern for “stacked mini-tables.”
- The “click stat to re-rank” interaction fits the OOTP mental model.

What I’d tighten next:
- Standardize the leaders “table strip” layout into the same ColumnSpec pattern used for standings, so future leaderboards can share code.
- Make the “active stat” or “current sort” state visually explicit (small highlight), because it’s a workflow surface.

---

## 6) Recommendations (prioritized)

### Tier 1 — hardening the panel contract (highest ROI)
1) **Narrow PanelChrome API** (reduce drift risk).
2) **Auto-visibility as default** for secondary/tertiary bars (content-driven).
3) **Extract ColumnSpec** into a shared module and migrate leaders to it.

### Tier 2 — root-cause the 1px scroll mismatch without losing UX
4) Keep `MicroScrollGuard`, but add **diagnostic logging** + a test that asserts:
   - “if expected height fits, scroll range must be 0 or <= threshold”
5) Decide whether “table panels” should have an **exact vertical rhythm mode**.

### Tier 3 — scaling to many panels/pages
6) Decide your long-term plan for large tables:
   - continue with widget rows for “top N” lists
   - adopt `QAbstractItemModel + QTableView` for large, sortable datasets
7) Add a “panel cookbook” example panel in code that is as canonical as the docs claim it is (so new panels copy *the right thing*).

---

## 7) Bottom line

You are **meaningfully implementing the vision**—not just talking about it.

- The **shell** and **grid methodology** are real.
- **PanelChrome** is already the correct primitive and is being used as the default building block.
- The two flagship panels demonstrate the approach is viable and aesthetically consistent.
- Your main work now is **hardening the contract** so future pages can’t accidentally drift, and deciding how strict you want “pixel-perfect locked tables” to be across DPI environments.

If you do the Tier 1 items next, you’ll have a panel system that can scale to the full OOTP-like app without collapsing under its own UI entropy.


---

## Appendix A) Draft “protected” PanelChrome public API (proposal)

The goal is to keep composition ergonomic while preventing drift. A minimal, opinionated public surface might look like:

```python
panel = PanelChrome("LEAGUE STANDINGS", panel_variant="table")

panel.set_columns(StandingsHeaderRow())                 # tertiary-left
panel.set_filters(LeadersFilterBar(on_change=...))      # secondary-left
panel.set_body(LeagueStandingsWidget(...))              # body
panel.set_footer(text="View: Standard Standings | 32 Teams")

panel.add_action_right(MyIconButton(...))               # primary-right
panel.add_action_left(MyBreadcrumbsWidget(...))         # primary-left extras (rare)
```

Internally, `PanelChrome` owns:
- clearing/replacing slots (so repeated calls don’t pile widgets)
- visibility (bars auto-show when content is present)
- variant-specific padding (table/card)
- common affordances (footer meta text, right-side buttons)

This keeps pages from reaching into `panel.header_secondary.add_left(...)` directly.

---

## Appendix B) Debug instrumentation for the 1px scroll case

A lightweight debugging helper (even if only enabled in dev mode) will save you hours:

- Log the scroll viewport height vs content `sizeHint()`
- Log scroll range (`vbar.maximum()`)
- Log “expected height” based on row count × `ROW_H`

When the issue shows up, you’ll know whether the mismatch is:
- border/padding,
- font metrics,
- layout rounding,
- or grid pitch.

Even better: write a small UI test that asserts “range <= 1” for known-fit cases and fails if it grows.

