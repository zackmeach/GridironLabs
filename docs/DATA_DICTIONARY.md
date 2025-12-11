# Data Dictionary (v0)

High-level fields for current Parquet schemas. Units are as noted; extend as schemas evolve.

## Players
- `player_id` (str), `name` (str), `position` (str), `team` (str), `era`/`season` (int)
- Ratings: `overall`, `athleticism`, `technical`, `intangibles`, `potential` (0–100)
- Core stats (examples): `passing_yards`, `passing_tds`, `interceptions`, `rushing_yards`, `rushing_tds`, `receiving_yards`, `receiving_tds`, `tackles`, `sacks`, `forced_fumbles`, `def_interceptions`
- Provenance: `source`, `pull_timestamp`, `schema_version`, `refresh_id`

## Teams
- `team_id` (str), `name` (str), `era`/`season` (int)
- Ratings: `overall`, `offense_rating`, `defense_rating`, `special_teams_rating`
- Standings: `wins`, `losses`, `ties`, `points_for`, `points_against`
- Efficiency (examples): `epa_off`, `epa_def`, `success_rate_off`, `success_rate_def`
- Provenance: `source`, `pull_timestamp`, `schema_version`, `refresh_id`

## Coaches
- `coach_id` (str), `name` (str), `team` (str), `tenure_start`, `tenure_end`
- Ratings: `tactics`, `development`, `leadership`, `overall`
- Records: `wins`, `losses`, `ties`, `playoff_wins`, `playoff_losses`
- Provenance fields as above

## Games
- `game_id` (str), `season` (int), `week` (int), `is_postseason` (bool), `playoff_round` (str)
- Teams: `home_team`, `away_team`; Location: `venue`, `city`
- Timing: `start_time` (datetime), `status` (`scheduled`|`in_progress`|`final`)
- Scores: `home_score`, `away_score`
- Provenance fields as above

## Notes
- Schemas are versioned (`schema_version`); update this doc and append to `docs/CHANGELOG.md` when fields change.
