# docs

Documentation starters:

- `ARCHITECTURE.md` — high-level flow and layering, including the current UI bootstrap steps and navigation history/search hooks.
- `DATA_DICTIONARY.md` — schema fields, units, and versions.
- `ARCHITECTURE_DIAGRAM.md` — text diagram of sources → data → services → UI.
- `CHANGELOG.md` — release notes and schema/UI changes.
- `CONTRIBUTING.md` — expectations for collaborators and tooling.
- `UI_CONTRACT.md` — source-of-truth UI composition + persistence conventions (includes a glossary for key terms like `panelVariant` and `scrollVariant`).
- `ui_panels.md` — how to build pages using the panel framework.
- `scripts/ui_snapshot.py` — deterministic UI snapshot CLI (PNG + JSON) targeting page/panel `objectName`s; outputs land in `ui_artifacts/`.
- Windows note: ensure `pyside6` and `polars` are installed in your venv (`pip install pyside6 polars`).
- UI note: context bar is 2x nav height and holds all page titles; nav/context share the same surface color. Pages render their content via panel cards placed on a grid canvas. Navigation history (back/forward) and search are wired through the top nav; the home dashboard drives team/player summary navigation. Settings includes a basic settings-form reference surface (TabStrip + FormGrid).
- UI layout notes live alongside code in `src/gridironlabs/ui/README.md`, `UI_COMPONENT_NOMENCLATURE.md`, and `docs/ui_panels.md`.
