# Data Dictionary (stub)

Document schema fields, definitions, and units here. Suggested sections:

- **Players**: id, name, position, team, era/season, ratings (overall/athleticism/technical/intangibles/potential), stat fields (traditional/advanced).
- **Teams**: id, name, era/season, ratings, standings metrics, efficiency metrics.
- **Coaches**: id, name, team/tenure, ratings, records.
- **Games**: id, season, week, home_team, away_team, location, start_time, status (`scheduled`/`final`), is_postseason, playoff_round (e.g., Wild Card/Divisional/Conference/Super Bowl), home_score, away_score.
- **Provenance**: source, pull_timestamp, schema_version, refresh_id.

Add a changelog entry whenever schema versions change.
