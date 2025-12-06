"""Repository interfaces for Parquet-backed entity summaries."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Protocol

from gridironlabs.core.errors import DataValidationError, NotFoundError
from gridironlabs.core.models import EntitySummary
from gridironlabs.data.schemas import SchemaVersion


class SummaryRepository(Protocol):
    """Abstraction for supplying summaries to services and UI layers."""

    def iter_players(self) -> Iterable[EntitySummary]: ...

    def iter_teams(self) -> Iterable[EntitySummary]: ...

    def iter_coaches(self) -> Iterable[EntitySummary]: ...

    def get_player(self, player_id: str) -> EntitySummary: ...

    def get_team(self, team_id: str) -> EntitySummary: ...

    def get_coach(self, coach_id: str) -> EntitySummary: ...


class ParquetSummaryRepository:
    """Skeleton Parquet-backed implementation."""

    def __init__(self, root: Path, schema_version: SchemaVersion) -> None:
        self.root = root
        self.schema_version = schema_version

    def _load_table(self, name: str) -> Iterable[EntitySummary]:
        raise NotImplementedError("Parquet loading will be implemented later.")

    def iter_players(self) -> Iterable[EntitySummary]:
        return self._load_table("players")

    def iter_teams(self) -> Iterable[EntitySummary]:
        return self._load_table("teams")

    def iter_coaches(self) -> Iterable[EntitySummary]:
        return self._load_table("coaches")

    def get_player(self, player_id: str) -> EntitySummary:
        for player in self.iter_players():
            if player.id == player_id:
                return player
        raise NotFoundError(f"Player {player_id} not found")

    def get_team(self, team_id: str) -> EntitySummary:
        for team in self.iter_teams():
            if team.id == team_id:
                return team
        raise NotFoundError(f"Team {team_id} not found")

    def get_coach(self, coach_id: str) -> EntitySummary:
        for coach in self.iter_coaches():
            if coach.id == coach_id:
                return coach
        raise NotFoundError(f"Coach {coach_id} not found")

    def validate_schema(self) -> None:
        """Placeholder for schema validation logic."""
        raise DataValidationError("Parquet schema validation is not implemented yet.")
