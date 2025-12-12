# docs

Documentation starters:

- `ARCHITECTURE.md` — high-level flow and layering.
- `DATA_DICTIONARY.md` — schema fields, units, and versions.
- `ARCHITECTURE_DIAGRAM.md` — text diagram of sources → data → services → UI.
- `CHANGELOG.md` — release notes and schema/UI changes.
- `CONTRIBUTING.md` — expectations for collaborators and tooling.
- Windows note: ensure `pyside6` and `polars` are installed in your venv (`pip install pyside6 polars`).
- UI note: context bar is 2x nav height and holds all page titles; nav/context/panels share the same surface color. Panels use a shared `PanelCard` shell (optional title with white separator).
- UI layout notes (including the static Settings mock) live alongside code in `src/gridironlabs/ui/README.md` and `UI_COMPONENT_NOMENCLATURE.md`.
