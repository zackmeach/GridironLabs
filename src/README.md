# src

Source tree for the Gridiron Labs application. Follows a layered layout:

- `gridironlabs/core` — configuration, logging, domain types, shared errors.
- `gridironlabs/data` — Parquet schemas and data-source adapters.
- `gridironlabs/services` — app-facing services (search, summaries).
- `gridironlabs/ui` — PySide6 desktop shell and widgets, including the reusable Page → GridCanvas → PanelChrome framework (panel system scaffolding).
- `gridironlabs/resources` — themes and future assets.
