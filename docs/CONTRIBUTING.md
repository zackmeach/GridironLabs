# Contributing (agent-friendly)

- Use feature branches; open small PRs with context on scope and testing.
- Keep public functions typed; lint with `ruff` and type-check with `mypy`.
- Tests: `pytest` (unit/integration/ui) with fixtures for Parquet/HTTP mocks.
- Data: prefer Parquet; document schema changes in `DATA_DICTIONARY.md`.
- UI: follow dark theme, keyboard navigation, and state panels for loading/empty/error.
- Logging: use the app logger with correlation ids when running data pulls.
