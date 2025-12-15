# data/processed

Canonical, schema-validated Parquet tables consumed by repositories and UI.

- Seed quickly for local UI testing: `python scripts/generate_fake_nfl_data.py`
- If empty, the app still boots; context stats will be zero and the matchup ticker may have no items.