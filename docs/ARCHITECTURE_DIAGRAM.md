# Architecture Diagram (text)

```text
┌──────────────────────────────┐
│  Sources                     │
│  - nflreadpy                 │
│  - PFR scraping              │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│  Scripts                     │
│  - refresh_data              │
│  - generate_fake_nfl_data    │
└───────────────┬──────────────┘
                │ raw/interim
                ▼
┌──────────────────────────────┐
│  Normalization & Validation  │
│  - schema versions           │
│  - provenance                │
└───────────────┬──────────────┘
                │ processed Parquet
                ▼
┌──────────────────────────────┐
│  ParquetSummaryRepository    │
│  - players/teams/coaches     │
│  - games (schedules/scores)  │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│  Services                    │
│  - search (in-memory)        │
│  - summary                   │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│  UI (PySide6)                │
│  - NavigationBar + Context   │
│  - Stacked pages             │
│    - Settings: form surface  │
│    - Others: placeholders    │
│  - Context bar 2x nav, holds │
│    titles; no titles in body │
│  - Nav/context share surface │
│    color                     │
└──────────────────────────────┘
```

Notes:
- Context bar height is 2x nav and includes a leading icon slot.
- Pages are built with the Page → GridCanvas → PanelChrome framework.
- High-row-count tables are validated via a dev-only Table Demo surface (`page-table-demo`) using `OOTPTableView`.

