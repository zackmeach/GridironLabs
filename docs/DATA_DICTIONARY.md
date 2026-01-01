# Data Dictionary (v0)

High-level fields for the current Parquet schemas under `data/processed`.
These tables are consumed by `gridironlabs.data.repository.ParquetSummaryRepository`.

## players.parquet

**Required columns (v0):** `id`, `name`, `position`, `team`, `era`, `ratings`, `stats`

- **id** (str): stable player identifier
- **name** (str)
- **position** (str)
- **team** (str): team abbreviation (e.g., `GB`)
- **era** (str): season label (currently stringified year, e.g., `2025`)
- **ratings** (struct/map): `overall`, `athleticism`, `technical`, `intangibles`, `potential` (0–100)
- **stats** (struct/map): numeric stat keys (examples used by the Home **League Leaders** panel):\n+  - Passing: `passing_yards`, `passing_completions`, `passing_attempts`, `passing_tds`, `interceptions`, `qbr`, `wpa_total`\n+  - Rushing: `rushing_yards`, `rushing_attempts`, `rushing_tds`, `fumbles`, `rush_20_plus`, `wpa_total`\n+  - Receiving: `receiving_yards`, `receptions`, `receiving_targets`, `receiving_tds`, `receiving_yac`, `fumbles`, `wpa_total`\n+  - Kicking: `field_goals_made`, `field_goals_attempted`, `fg_made_under_29`, `fg_made_30_39`, `fg_made_40_49`, `fg_made_50_plus`, `wpa_total`\n+  - Defense: `tackles`, `tackles_for_loss`, `sacks`, `forced_fumbles`, `def_interceptions`, `passes_defended`, `wpa_total`\n+\n+  Other example keys (still used by scripts/UI scaffolds): `punts`, `punt_yards`

**Optional common metadata (when present):** `entity_type`, `schema_version`, `source`, `updated_at`

## teams.parquet

**Required columns (v0):** `id`, `name`, `era`, `ratings`, `stats`, `logo_url`, `logo_path`

- **id** (str): stable team identifier
- **name** (str): display name (e.g., `Green Bay Packers`)
- **era** (str): season label (currently stringified year)
- **ratings** (struct/map): includes `overall` plus any additional team rating facets
- **stats** (struct/map): standings/efficiency metrics (examples: `wins`, `losses`, `points_for`, `points_against`)
- **logo_url** (str | null): Source URL for the team logo (e.g., from nflreadpy/ESPN).
- **logo_path** (str | null): Local path to the cached logo image (e.g., `data/external/logos/GB.png`).

**Optional common metadata (when present):** `team` (abbr), `entity_type`, `schema_version`, `source`, `updated_at`

## coaches.parquet

**Required columns (v0):** `id`, `name`, `team`, `era`, `ratings`, `stats`

- **id** (str): stable coach identifier
- **name** (str)
- **team** (str): team abbreviation
- **era** (str): season label
- **ratings** (struct/map): coaching ratings facets
- **stats** (struct/map): record/performance fields (examples: `wins`, `losses`, `playoff_prob`)

**Optional common metadata (when present):** `entity_type`, `schema_version`, `source`, `updated_at`

## games.parquet

**Required columns (v0):**
`id`, `season`, `week`, `home_team`, `away_team`, `location`, `start_time`, `status`, `is_postseason`, `playoff_round`, `home_score`, `away_score`

- **id** (str): stable game identifier
- **season** (int)
- **week** (int)
- **home_team** / **away_team** (str): team abbreviations
- **location** (str)
- **start_time** (datetime)
- **status** (str): currently `scheduled` or `final` in the scaffold
- **is_postseason** (bool)
- **playoff_round** (str | null)
- **home_score** / **away_score** (int | null)

**Optional common metadata (when present):** `schema_version`, `source`

## Notes

- Schemas are versioned in `src/gridironlabs/data/schemas.py` (`SCHEMA_REGISTRY`).
- When fields change, update this doc and append a note to `docs/CHANGELOG.md`.
