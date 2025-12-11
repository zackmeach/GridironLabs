# data/processed

Canonical, schema-validated Parquet tables consumed by repositories and UI.

- Seed quickly for local UI testing: `python scripts/generate_fake_nfl_data.py`
- If empty, the app will surface an offline/banner warning and stub views until data is generated.