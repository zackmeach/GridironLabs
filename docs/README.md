# docs

Documentation starters:

- `ARCHITECTURE.md` — high-level flow and layering.
- `DATA_DICTIONARY.md` — schema fields, units, and versions.
- `ARCHITECTURE_DIAGRAM.md` — text diagram of sources → data → services → UI.
- `CHANGELOG.md` — release notes and schema/UI changes.
- `CONTRIBUTING.md` — expectations for collaborators and tooling.
- `ui_panels.md` — how to build pages using the panel framework.
- Windows note: ensure `pyside6` and `polars` are installed in your venv (`pip install pyside6 polars`).
- UI note: context bar is 2x nav height and holds all page titles; nav/context share the same surface color. Pages render their content via panel cards placed on a grid canvas (Settings is the reference page).
- UI layout notes live alongside code in `src/gridironlabs/ui/README.md`, `UI_COMPONENT_NOMENCLATURE.md`, and `docs/ui_panels.md`.
