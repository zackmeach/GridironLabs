# scripts

Operational utilities:

- `refresh_data.py` — downloads team logos via `nflreadpy` and enriches `data/processed/teams.parquet` with `logo_path` / `logo_url`.
- `generate_fake_nfl_data.py` — builds synthetic rosters/stats and a games schedule so UI features (like the matchup ticker and future dashboards) have data when you are offline. It emits `games.parquet` with home/away, location, kickoff time, status, scores, and playoff round.
- Future generators (synthetic data) and maintenance tasks belong here.

Prereqs: activate the venv and ensure `polars` and `pyside6` are installed (`pip install -e .[dev]` plus `pip install pyside6 polars` on Windows if needed).

## Logo refresh (current behavior)

`refresh_data.py` currently focuses on **team logos**:

- Downloads team logos to `data/external/logos/` (via `nflreadpy` ESPN logo URLs).
- Enriches `data/processed/teams.parquet` by filling `logo_path` / `logo_url` for each team (across all seasons in that file).

Run:

```bash
python scripts/refresh_data.py
```

Note: this is a partial refresh; full ingestion/merge/validation across all entity tables is still TBD.