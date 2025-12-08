"""Repository interfaces for Parquet-backed entity summaries."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Protocol

from gridironlabs.core.errors import DataValidationError, MissingDependencyError, NotFoundError
from gridironlabs.core.models import EntitySummary, GameSummary
from gridironlabs.data.schemas import SchemaVersion


class SummaryRepository(Protocol):
    """Abstraction for supplying summaries to services and UI layers."""

    def iter_players(self) -> Iterable[EntitySummary]: ...

    def iter_teams(self) -> Iterable[EntitySummary]: ...

    def iter_coaches(self) -> Iterable[EntitySummary]: ...

    def iter_games(self) -> Iterable[GameSummary]: ...

    def get_player(self, player_id: str) -> EntitySummary: ...

    def get_team(self, team_id: str) -> EntitySummary: ...

    def get_coach(self, coach_id: str) -> EntitySummary: ...


class ParquetSummaryRepository:
    """Parquet-backed implementation used by services and UI."""

    def __init__(self, root: Path, schema_version: SchemaVersion) -> None:
        self.root = root
        self.schema_version = schema_version
        self._cache: dict[str, list[EntitySummary]] = {}

    def _path_for(self, name: str) -> Path:
        return self.root / f"{name}.parquet"

    def _normalize_date(self, raw: object) -> date | None:
        if raw is None:
            return None
        if isinstance(raw, date):
            return raw
        if isinstance(raw, datetime):
            return raw.date()
        if isinstance(raw, str):
            try:
                return date.fromisoformat(raw)
            except ValueError:
                return None
        return None

    def _normalize_datetime(self, raw: object) -> datetime | None:
        if raw is None:
            return None
        if isinstance(raw, datetime):
            return raw
        if isinstance(raw, date):
            return datetime.combine(raw, datetime.min.time())
        if isinstance(raw, str):
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(raw, fmt)
                except ValueError:
                    continue
        return None

    def _load_table(self, name: str) -> Iterable[EntitySummary]:
        if name in self._cache:
            return self._cache[name]

        path = self._path_for(name)
        if not path.exists():
            raise NotFoundError(f"Parquet table {name} not found at {path}")

        try:
            import polars as pl
        except ImportError as exc:  # pragma: no cover - optional dependency at runtime
            raise MissingDependencyError("polars is required to load Parquet datasets") from exc

        try:
            df = pl.read_parquet(path)
        except Exception as exc:  # pragma: no cover - surface IO errors
            raise DataValidationError(f"Failed to read Parquet table {name}: {exc}") from exc

        required_columns = {"id", "name"}
        missing = required_columns.difference(set(df.columns))
        if missing:
            raise DataValidationError(f"Table {name} is missing columns: {', '.join(sorted(missing))}")

        records: list[EntitySummary] = []
        for row in df.to_dicts():
            entity_type = row.get("entity_type") or name.rstrip("s")
            ratings = row.get("ratings")
            stats = row.get("stats")
            records.append(
                EntitySummary(
                    id=str(row["id"]),
                    name=str(row["name"]),
                    entity_type=str(entity_type),
                    era=str(row.get("era") or ""),
                    team=(row.get("team") or None),
                    position=(row.get("position") or None),
                    ratings=ratings,  # type: ignore[arg-type]
                    stats=stats,  # type: ignore[arg-type]
                    schema_version=str(row.get("schema_version") or self.schema_version.version),
                    source=row.get("source"),
                    updated_at=self._normalize_date(row.get("updated_at")),
                )
            )

        self._cache[name] = records
        return records

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

    def iter_games(self) -> Iterable[GameSummary]:
        cache_key = "games"
        if cache_key in self._cache:
            return self._cache[cache_key]  # type: ignore[return-value]

        path = self._path_for("games")
        if not path.exists():
            raise NotFoundError(f"Parquet table games not found at {path}")

        try:
            import polars as pl
        except ImportError as exc:  # pragma: no cover - optional dependency at runtime
            raise MissingDependencyError("polars is required to load Parquet datasets") from exc

        try:
            df = pl.read_parquet(path)
        except Exception as exc:  # pragma: no cover - surface IO errors
            raise DataValidationError(f"Failed to read Parquet table games: {exc}") from exc

        required = {"id", "season", "week", "home_team", "away_team", "start_time", "status"}
        missing = required.difference(set(df.columns))
        if missing:
            raise DataValidationError(f"Table games is missing columns: {', '.join(sorted(missing))}")

        games: list[GameSummary] = []
        for row in df.to_dicts():
            start_time = self._normalize_datetime(row.get("start_time"))
            if start_time is None:
                raise DataValidationError(f"Invalid start_time for game {row.get('id')}")
            games.append(
                GameSummary(
                    id=str(row["id"]),
                    season=int(row.get("season") or 0),
                    week=int(row.get("week") or 0),
                    home_team=str(row["home_team"]),
                    away_team=str(row["away_team"]),
                    location=str(row.get("location") or ""),
                    start_time=start_time,
                    status=str(row.get("status") or "scheduled"),
                    is_postseason=bool(row.get("is_postseason") or False),
                    home_score=row.get("home_score"),
                    away_score=row.get("away_score"),
                    playoff_round=str(row.get("playoff_round") or "") or None,
                )
            )

        self._cache[cache_key] = games  # type: ignore[assignment]
        return games

    def validate_schema(self) -> None:
        """Placeholder for schema validation logic."""
        raise DataValidationError("Parquet schema validation is not implemented yet.")
