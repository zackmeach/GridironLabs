# ui/

PySide6 UI built to mirror OOTP26 layout conventions.

- `main_window.py` assembles the shell with a persistent top navigation bar, stacked content area, and reusable placeholder states (loading/empty/error).
- `widgets/` hosts reusable components (navigation bar, banners, future panels/cards).
- Styles are loaded from `resources/styles`.

Extend by adding tabbed sections for players, teams, coaches, drafts, and league overview.
