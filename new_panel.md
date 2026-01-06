# League Schedule panel jump-off (agent notes)

Goal: add a full-height League Schedule panel to Home alongside standings/leaders with week navigation.

## UX rules

- Layout: three panels across Home (standings, leaders, schedule on the right). Stable IDs: `panel-league-standings`, `panel-league-leaders`, `panel-league-schedule`.
- Header: panel variant `table` with week navigator in the primary-right slot.
- Body: grouped by week/day; shows date bars with column labels (Date | Home | Away | Time | Score) and rows with team logos/names plus kickoff time or final score.
- Empty state: "No games loaded. Generate data with scripts/generate_fake_nfl_data.py."

## Data requirements

- `games.parquet` entries exposed via `ParquetSummaryRepository.iter_games()`; fields used: `season`, `week`, `start_time`, `status`, `home_team`, `away_team`, `home_score`, `away_score`, `is_postseason`, `playoff_round`.
- Week grouping prefers the latest season in the dataset; postseason rounds map to readable labels.

## Files touched

- `src/gridironlabs/ui/main_window.py` (Home layout + week navigator wiring)
- `src/gridironlabs/ui/widgets/schedule.py` (LeagueScheduleWidget and navigator)
- Docs: `README.md`, `UI_COMPONENT_NOMENCLATURE.md`, `docs/ARCHITECTURE.md`
- Tests: `tests/ui/test_schedule_widget.py`
