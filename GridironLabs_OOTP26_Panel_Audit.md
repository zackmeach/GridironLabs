# GridironLabs: OOTP26 Panel Pattern Audit & Forward-Looking PanelChrome Recommendations
*(Based on the provided OOTP26 panel screenshots + your repo docs/source as of early Jan 2026.)*

## 0) Why this audit matters (ties back to your vision)

Your canonical vision doc frames **PanelChrome as the single reusable UI primitive**: a strict vertical stack of header bars + a dense body, meant to cover the “full range of OOTP patterns” without spawning bespoke panel types (Primary/Secondary/Tertiary headers, body API, section bars, future QTableView migration, persistence).  
This audit is about **getting ahead of future drift** by studying the *actual* panel/content patterns OOTP26 uses and stress-testing your current PanelChrome contract against them.

**Key vision constraints I’m treating as non‑negotiable:**
- **Single source of truth** for panel chrome and bar behavior (PanelChrome + PanelBars).
- **Composable header bars** (slot-based left/right clusters) instead of feature-specific headers.
- **Dense, professional, “GM workstation” feel**: tight rhythm, consistent insets, actionable rows, predictable grouping.
- **Two rendering strategies**: QWidget-per-row for small tables; model/view (QTableView) for large tables.

---

## 1) Methodology / plan (how I approached the screenshots)

1) **Normalize what “a panel” means in OOTP**  
   I treated each screenshot as a composition of a few recurring primitives:
   - chrome (title row, dropdowns, collapsers)
   - toolbars/filter rows
   - column headers / sortable headers
   - body archetype (table, list, key/value, charts, forms)
   - internal grouping (section bars, separators)
   - selection/hover semantics
   - footers (meta text, action buttons, pagination)

2) **Build a taxonomy** of reusable sub-patterns (so you don’t implement 23 one-off bodies).

3) **Map each screenshot** → (a) which reusable primitives it needs, (b) what your current system already supports, (c) the minimum safe changes that improve future coverage.

4) **Prioritize changes** by:
   - how often the pattern appears in OOTP (high frequency = high priority)
   - how likely it is to be needed early in GridironLabs (players/teams pages)
   - architectural leverage (1 change unlocks many panels)
   - performance risk (large datasets)

---

## 2) What OOTP26 is “really doing” (high-level panel grammar)

Across the screenshots, OOTP panels overwhelmingly fall into **four families**:

### A) Dense data surfaces (tables + lists)
These are the core of the UI:
- **Large tables** with many columns and hundreds/thousands of rows (rosters, logs, history)  
- **Small/medium tables** that need pixel-perfect custom rows (standings, leaders, depth charts)  
- **Rich lists** (avatar + multi-line text + right aligned badge)

### B) Grouped bodies (sectioned stacks)
A single panel often contains multiple stacked sections:
- section bar (“Rotation”, “Bullpen”, “Past Yrs.”)
- optional section-specific column header row
- rows
This is extremely common (Roster/Depth charts, multi-section stat histories).

### C) Detail panels (key/value + progress bars)
Player/team details are mostly “forms” or “read-only forms”:
- key/value rows
- mixed inline icons (flags/emoji)
- rating/progress bars, sometimes current vs potential
- occasional dropdowns embedded inside the body

### D) “Utility” panels (charts, scoreboards, text/action menus, settings forms)
- charts and graphs
- last game scoreboard blocks
- scrollable action feeds / rich text

---

## 3) “Gap analysis”: what to adjust now (PanelChrome-level changes)

Your current approach (PanelChrome + Primary/Secondary/Tertiary/Footer bars + body API + QSS-driven styling) is **exactly the right direction**. Most gaps are not about “new panel types” — they’re about **slightly expanding the bar/body capabilities** so future panels remain composable.

---

### 3.1 Make the **Primary header** capable of “Title + Left Controls + Right Controls”
OOTP frequently puts dropdowns *in the title row* (team selector on left, rating-view on right).

**Recommendation**
- Keep title label, but allow inserting widgets:
  - `PrimaryHeaderBar.add_left(widget, *, after_title: bool = True)`
  - `PrimaryHeaderBar.add_right(widget)`
- Treat “View/Mode/Season” as **standard header actions** (QToolButton + QMenu), but don’t require them; panels decide.

**Why now:** This avoids pushing everything into Secondary header, and keeps the OOTP “single-row” table headers possible.

---

### 3.2 Standardize a **Filter/Toolbar row** pattern (usually Secondary header)
OOTP uses compact dropdown toolbars constantly (View / Filter / Position / Dates / Reset…).

**Recommendation**
- Keep using Secondary header, but create a **single reusable toolbar widget** that can be dropped into Secondary:
  - `CompactFilterBar` (horizontal layout, compact comboboxes, consistent height, optional right-aligned summary text)
  - include a “Reset” affordance pattern (button or toolbutton)
- Add an overflow strategy:
  - either allow it to wrap (not very OOTP), or
  - use horizontal scrolling inside the bar, or
  - shrink combo widths + elide (closest to OOTP).

**Why now:** Prevents every page inventing its own spacing, heights, and combo style.

---

### 3.3 Expand SectionBar into a **real** OOTP “Section header row”
You already have a `SectionBar` class, but OOTP section bars often carry **right-aligned column labels** (e.g., “AVG HR RBI”) and sometimes section-level controls.

**Recommendation**
- Ensure `SectionBar` supports both left title and right content (it already has slots structurally; enforce styling + usage).
- Provide a small helper:
  - `SectionColumnsRow(columns: list[ColumnSpec])` or `SectionBar.set_right_columns([...])` (optional)
- Add QSS to render the gold/orange bar style consistently.

**Why now:** Sectioned stacks are everywhere (Roster, History, multi-table panels).

---

### 3.4 Table strategy: formalize “small table” vs “large table”
You’re already thinking this way; the screenshots confirm it’s essential.

**Recommendation**
- Keep QWidget-per-row for:
  - standings, leaders, depth charts, “top N” lists, small sub-tables
- Introduce an `OOTPTableView` wrapper for:
  - rosters, logs, search results, player histories with many seasons/games
  - with a custom header style, row height, and a ColumnSpec-driven model
- Add support for:
  - **summary rows** (TOTAL / AVG / Career Highs)
  - **group header rows** inside tables (e.g., “Season”, “Past Yrs.”)
  - **icons/emoji/flags** in cells (delegate rendering)

**Why now:** This is the single biggest future performance pitfall.

---

### 3.5 Body scroll policy: “locked surface” should be a reusable wrapper
OOTP uses scrolling constantly, and your README mentions “locked surface” scroll behavior.

**Recommendation**
- Provide a standard helper:
  - `make_locked_scroll(widget) -> QScrollArea` that sets `scrollVariant="hidden"` + correct margins + wheel behavior.
- Encourage panel bodies to either:
  - be inherently scrollable (TableView), or
  - be wrapped by this helper, but **don’t** let every widget invent scroll config.

---

## 4) Widget library additions (body archetypes you will definitely need)

These should live under `src/gridironlabs/ui/widgets/` as reusable, panel-agnostic building blocks.

### 4.1 `KeyValueList` (read-only form rows)
Supports alternating row stripes, icons in values, right alignment, and optional “value widget” (dropdown).

Used by: Personal Details, Status, Summary, Team Finances grids.

### 4.2 `RatingBarRow` / `RatingBarsPanel`
Supports:
- single value bars (defensive ratings)
- dual bars (current vs potential)
- consistent label/value placement

### 4.3 `IconTextList` (avatar + multi-line + right badge)
Used by: Top Prospects, Minor League System, Hot/Not, Leaders blocks.

### 4.4 `ScoreboardWidget` (mini scoreboard table)
Used by: Your Last Game.

### 4.5 `ChartPanelBody`
Used by: Division Graph, trends.

### 4.6 `FormGrid` (settings-like two-column form)
Used by: Play Mode / Team Control Settings.

---

## 5) Per-screenshot breakdown (what each panel implies)

Below, each entry lists:
- **Observed content pattern**
- **Reusable primitives**
- **What to change / add** (preferably at the primitive/widget layer, not per-panel hacks)

---

### OOTP Panel 01 — Team Roster (sectioned table stack)
**Observed**
- Single panel contains multiple sections: “Lineup vs RHP”, “Rotation”, “Bullpen”
- Each section has its own mini header row + aligned columns
- Selection highlight + role/badges

**Primitives**
- `SectionBar` (left title + right columns)
- `ColumnSpec` shared between header and row rendering
- Selection/hover states

**Needed changes**
- Make `SectionBar` styling + right-slot usage first-class
- Consider a `TableStackBody` helper: (section bar + header row + rows) repeated

---

### OOTP Panel 02 — Who’s Hot / Who’s Not (two-section list)
**Observed**
- Two section headers, each with a short list of rows
- Row = name left, stat line right

**Primitives**
- `SectionBar`
- `CompactStatRow` (label + right-aligned value)

**Needed changes**
- None at PanelChrome level; add reusable list row widget

---

### OOTP Panel 03 — Your Last Game (status strip + scoreboard + action footer)
**Observed**
- Callout strip (“LOSS”, date)
- Embedded scoreboard grid
- Footer with 3 large buttons

**Primitives**
- `CalloutStrip` (status pill)
- `ScoreboardWidget`
- Footer actions (already possible via FooterBar)

**Needed changes**
- Ensure FooterBar styling supports “button row” cleanly
- Provide ScoreboardWidget for reuse

---

### OOTP Panel 04 — Action Menu (scrollable rich text)
**Observed**
- Scrollable text with link-style affordances

**Primitives**
- `QTextBrowser` / rich text widget
- Scroll variant visible (or hidden)

**Needed changes**
- Standardize `RichTextPanelBody` helper
- Decide when scrollbars should be visible vs “hidden”

---

### OOTP Panel 05 — Division Graph (chart body)
**Observed**
- A plot/chart inside panel

**Primitives**
- `ChartPanelBody`

**Needed changes**
- Add a chart embedding strategy (matplotlib canvas / QtCharts)
- Provide a “chart” panel variant for padding defaults (optional)

---

### OOTP Panel 06 — Team Finances (mixed key/value + progress bars, scroll)
**Observed**
- Mixed layout: logo, summary text, key/value grid, “Market Information” bars
- Scrollable

**Primitives**
- `KeyValueList`
- `ProgressBarRow`
- `make_locked_scroll`

**Needed changes**
- Build these widgets now; this will be very common on Team pages

---

### OOTP Panel 07 — Team Pitching Leaders (repeating leader blocks w/ headshot)
**Observed**
- Category blocks (ERA, Wins, etc.), each with image + short list

**Primitives**
- `LeaderCategoryBlock` (image + header + rows)

**Needed changes**
- A reusable “leaders block” widget (you already have a leaders table; this is a different presentation archetype)

---

### OOTP Panel 08 — Team Stats Rankings (compact stat grid)
**Observed**
- Dense two-column stat ranking list (value + label + rank)

**Primitives**
- `StatGrid`

**Needed changes**
- Add `StatGrid` widget for Team overview pages

---

### OOTP Panel 09 — Active Roster table (title bar + dropdown)
**Observed**
- Title bar includes right dropdown
- Table: fixed header, row selection circles, icons, many rows

**Primitives**
- `PrimaryHeaderBar` right controls
- `OOTPTableView` (model/view)

**Needed changes**
- Expand PrimaryHeaderBar slots
- Start QTableView wrapper work

---

### OOTP Panel 10 — Player list with toolbar filters
**Observed**
- Toolbar row: VIEW / FILTER / POSITION / SCOUTING / REPORT
- Table below

**Primitives**
- Secondary header toolbar widget
- `OOTPTableView`

**Needed changes**
- Standardize the toolbar widget (spacing, height, eliding)

---

### OOTP Panel 11 — Minor League System (logo list w/ multi-line text)
**Observed**
- List rows with left icon and multiple text lines

**Primitives**
- `IconTextList`

**Needed changes**
- Add `IconTextRow` building block (clickable)

---

### OOTP Panel 12 — BNN Top Prospects (scrolling rich list w/ right badge)
**Observed**
- Avatar left, multi-line, right aligned badge (level/team)
- Scrollbar

**Primitives**
- `IconTextList` with right badge
- `make_locked_scroll`

**Needed changes**
- None at chrome level; add widget archetype

---

### OOTP Panel 13 — Minor league roster (two dropdowns + table)
**Observed**
- Left dropdown (team) and right dropdown (ratings view) in same top bar
- Table with ratings columns

**Primitives**
- Primary header left + right controls
- `OOTPTableView`

**Needed changes**
- Primary header must support left-side widgets, not only title

---

### OOTP Panel 14 — Scouting list (toolbar + very wide table)
**Observed**
- Toolbar filters + very wide table (flags, icons, scouting accuracy)

**Primitives**
- Toolbar widget
- `OOTPTableView` with icon delegates + horizontal scrolling

**Needed changes**
- QTableView wrapper + delegate rendering for emoji/flags/icons

---

### OOTP Panel 15 — Personal Details (key/value table)
**Observed**
- Alternating stripes, key left, value right, icons inline

**Primitives**
- `KeyValueList`

**Needed changes**
- Add KeyValueList widget; extremely common on Player pages

---

### OOTP Panel 16 — Basic Pitching Ratings (current/potential bars)
**Observed**
- Dual-value bars (current/potential)

**Primitives**
- `RatingBarRow` (dual)

**Needed changes**
- Add dual-bar support and consistent color mapping strategy

---

### OOTP Panel 17 — Summary + dropdown + rating bars (mixed form)
**Observed**
- Key/value section + embedded dropdown + rating bars

**Primitives**
- `KeyValueList` that can host “value widgets”
- Rating bars

**Needed changes**
- KeyValueList should allow a QWidget in value column

---

### OOTP Panel 18 — Game log + Season totals + Past years (multi-table stack)
**Observed**
- A single panel contains:
  - Games table (w/ dropdown)
  - Season totals subtable
  - Past years subtable
- Shared column rhythm

**Primitives**
- `TableStackBody` (stacked subtables)
- OR `OOTPTableView` with group rows

**Needed changes**
- Decide a standard approach for “multi-section tables”
  - For small data: stacked custom widgets
  - For large data: group rows in QTableView

---

### OOTP Panel 19 — Status tab strip (segmented header inside body)
**Observed**
- Top strip with two “tabs” (STATUS / POPULARITY & MORALE)

**Primitives**
- `SegmentedTabBar` / `TabStrip`

**Needed changes**
- Provide a small reusable tab strip widget (likely used on Player/Team pages)

---

### OOTP Panel 20 — Defensive Ratings (single-value bars)
**Observed**
- List of rating bars with value labels

**Primitives**
- `RatingBarRow` (single)

**Needed changes**
- Same as Panel 16; share the rating bar system

---

### OOTP Panel 21 — Year-by-year stats + toolbar + summary rows
**Observed**
- Toolbar (View / League Scope / Split)
- Table with summary rows at end (TOTAL, 162 AVG, Career Highs)

**Primitives**
- Toolbar widget
- Table with summary rows

**Needed changes**
- QTableView wrapper should support summary rows (model-provided)

---

### OOTP Panel 22 — Game log filter toolbar (many controls) + table
**Observed**
- Big filter toolbar with league/team/date ranges + reset
- Table with many rows

**Primitives**
- Standard toolbar widget with overflow strategy
- Table view

**Needed changes**
- Invest in toolbar standardization early; otherwise every page drifts

---

### OOTP Panel 23 — Settings form (two-column controls + rich text + checkboxes)
**Observed**
- Page-like form: labels left, dropdowns right, explanatory text, section headers

**Primitives**
- `FormGrid`
- `RichTextBlock`

**Needed changes**
- Not a PanelChrome problem — it’s a reusable “settings form” layout widget

---

## 6) Suggested implementation roadmap (minimal regrets)

### Phase 0 — immediate “no-regrets” primitives (unlock lots of future panels)
- Collapsible PanelChrome (Primary header caret)
- Primary header supports left/right controls
- SectionBar styled + right-slot column support
- `make_locked_scroll()` helper
- `KeyValueList` widget
- `RatingBarRow` widget

### Phase 1 — standardize toolbars/filters (avoid drift)
- `CompactFilterBar` widget (secondary header)
- QSS for compact comboboxes/toolbuttons
- “Reset” pattern

### Phase 2 — Large table foundation
- `OOTPTableView` wrapper + ColumnSpec model
- Sorting, resizing, persistence hooks (QSettings keys)
- Icon/cell delegates (flags, emoji, badges)
- Summary rows + group rows

### Phase 3 — Finish the “utility” bodies
- ScoreboardWidget
- ChartPanelBody
- TabStrip widget
- FormGrid widget

---

## 7) Final guidance: how to avoid overfitting to screenshots

- **Do not clone OOTP layouts 1:1** as bespoke widget trees.  
  Instead: implement the 6–8 primitive archetypes above and compose them.
- Use screenshots to validate:
  - spacing rhythm (row height, header heights)
  - insets (single source of truth)
  - behavior (collapse, sorting, selection, persistence)
- If a new screenshot doesn’t fit your primitives, treat it as a signal that a primitive is missing — not that you need a one-off.

---

## Appendix: quick “coverage matrix” (by archetype)

- **Sectioned stacks**: 01, 02, 18
- **Rich lists**: 11, 12, 07
- **Key/value**: 15, 19, 17, 06
- **Rating bars**: 16, 20, 17
- **Toolbar + big table**: 09, 10, 13, 14, 21, 22, 18
- **Utility**: 03 (scoreboard), 05 (chart), 04 (rich text), 23 (settings form)
