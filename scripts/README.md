# scripts

Operational utilities:

- `refresh_data.py` — downloads team logos via `nflreadpy` and enriches `data/processed/teams.parquet` with `logo_path` / `logo_url`.
- `generate_fake_nfl_data.py` — builds synthetic rosters/stats and a games schedule so UI features (like the matchup ticker and Home dashboards) have data when you are offline. It emits `games.parquet` with home/away, location, kickoff time, status, scores, and playoff round.
  - Note: `rich` is optional; if it’s not installed the script falls back to plain printing and still generates datasets.
- Future generators (synthetic data) and maintenance tasks belong here.

Prereqs: activate the venv and ensure `polars` and `pyside6` are installed (`pip install -e .[dev]` plus `pip install pyside6 polars` on Windows if needed).

## Synthetic stats coverage (Home League Leaders)

`generate_fake_nfl_data.py` populates `players.parquet` with stat keys used by the Home **League Leaders** panel:

- Passing: `passing_yards`, `passing_completions`, `passing_attempts`, `passing_tds`, `interceptions`, `qbr`, `wpa_total`
- Rushing: `rushing_yards`, `rushing_attempts`, `rushing_tds`, `fumbles`, `rush_20_plus`, `wpa_total`
- Receiving: `receiving_yards`, `receptions`, `receiving_targets`, `receiving_tds`, `receiving_yac`, `fumbles`, `wpa_total`
- Kicking: `field_goals_made`, `field_goals_attempted`, `fg_made_under_29`, `fg_made_30_39`, `fg_made_40_49`, `fg_made_50_plus`, `wpa_total`
- Defense: `tackles`, `tackles_for_loss`, `sacks`, `forced_fumbles`, `def_interceptions`, `passes_defended`, `wpa_total`

## Logo refresh (current behavior)

`refresh_data.py` currently focuses on **team logos**:

- Downloads team logos to `data/external/logos/` (via `nflreadpy` ESPN logo URLs).
- Enriches `data/processed/teams.parquet` by filling `logo_path` / `logo_url` for each team (across all seasons in that file).

Run:

```bash
python scripts/refresh_data.py
```

Note: this is a partial refresh; full ingestion/merge/validation across all entity tables is still TBD.