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
│  - Home (Leaders grid)       │
│  - Section placeholders      │
│  - Settings mock (4/3/3)     │
│  - Context bar 2x nav, holds │
│    titles; no titles in body │
│  - Nav/context/panels share  │
│    surface color             │
└──────────────────────────────┘
```

Notes:
- Context bar height is 1.5x nav and includes a leading icon slot.
- Settings mock is cosmetic only; wiring comes later.

