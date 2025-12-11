# tests

Testing layout aligned to requirements:

- `unit/` — services, repositories, and utilities.
- `integration/` — Parquet read/write, scraping with HTTP mocking.
- `ui/` — pytest-qt smoke tests for windows/dialogs (nav + content stack).

Prereqs:
- Activate the venv and install dev deps: `pip install -e .[dev]`
- UI tests need PySide6 available; on Windows install explicitly if missing: `pip install pyside6`