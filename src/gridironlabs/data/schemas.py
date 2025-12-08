"""Schema definitions and versioning for Parquet datasets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class SchemaVersion:
    name: str
    fields: Sequence[str]
    version: str
    checksum: str | None = None


SCHEMA_REGISTRY: Mapping[str, SchemaVersion] = {
    "players:v0": SchemaVersion(
        name="players",
        version="v0",
        fields=("id", "name", "position", "team", "era", "ratings", "stats"),
        checksum=None,
    ),
    "teams:v0": SchemaVersion(
        name="teams",
        version="v0",
        fields=("id", "name", "era", "ratings", "stats"),
        checksum=None,
    ),
    "coaches:v0": SchemaVersion(
        name="coaches",
        version="v0",
        fields=("id", "name", "team", "era", "ratings", "stats"),
        checksum=None,
    ),
    "games:v0": SchemaVersion(
        name="games",
        version="v0",
        fields=(
            "id",
            "season",
            "week",
            "home_team",
            "away_team",
            "location",
            "start_time",
            "status",
            "is_postseason",
            "playoff_round",
            "home_score",
            "away_score",
        ),
        checksum=None,
    ),
}
