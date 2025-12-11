# scripts

Operational utilities:

- `refresh_data.py` — orchestrates pulls from nflreadpy/PFR into Parquet.
- `generate_fake_nfl_data.py` — builds synthetic rosters/stats so UI features (like the League Leaders grid) have data when you are offline. It now also emits a games schedule (regular season + postseason rounds) to `games.parquet` with home/away, location, kickoff time, status, scores, and playoff round.
- Future generators (synthetic data) and maintenance tasks belong here.

Prereqs: activate the venv and ensure `polars` and `pyside6` are installed (`pip install -e .[dev]` plus `pip install pyside6 polars` on Windows if needed).