"""Repository interfaces for Parquet-backed entity summaries.

`ParquetSummaryRepository` is the default implementation used by the UI/services.
It is intentionally lightweight: it loads Parquet tables from `data/processed`,
normalizes common fields, and provides simple in-memory caching.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol

from gridironlabs.core.errors import DataValidationError, MissingDependencyError, NotFoundError
from gridironlabs.core.models import EntitySummary, GameSummary, RatingBreakdown
from gridironlabs.data.schemas import SCHEMA_REGISTRY, SchemaVersion


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

    def __init__(
        self,
        root: Path,
        *,
        schema_version: str = "v0",
        schema_registry: Mapping[str, SchemaVersion] = SCHEMA_REGISTRY,
    ) -> None:
        self.root = Path(root)
        self.schema_version = str(schema_version).strip() or "v0"
        self.schema_registry = schema_registry

        self._entity_cache: dict[str, list[EntitySummary]] = {}
        self._games_cache: list[GameSummary] | None = None
        # O(1) id→index maps (rebuilt any time entity cache is loaded/reloaded)
        self._players_by_id: dict[str, int] = {}
        self._teams_by_id: dict[str, int] = {}
        self._coaches_by_id: dict[str, int] = {}

    def _path_for(self, name: str) -> Path:
        return self.root / f"{name}.parquet"

    def _schema_for(self, name: str) -> SchemaVersion | None:
        key = f"{name}:{self.schema_version}"
        fallback_key = f"{name}:v0"
        return self.schema_registry.get(key) or self.schema_registry.get(fallback_key)

    @staticmethod
    def _normalize_text(raw: object) -> str | None:
        if raw is None:
            return None
        text = str(raw).strip()
        return text or None

    @staticmethod
    def _as_int(raw: object) -> int | None:
        if raw is None:
            return None
        if isinstance(raw, bool):
            return int(raw)
        if isinstance(raw, int):
            return raw
        if isinstance(raw, float):
            return int(raw)
        try:
            return int(str(raw).strip())
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _as_float(raw: object) -> float | None:
        if raw is None:
            return None
        if isinstance(raw, bool):
            return float(int(raw))
        if isinstance(raw, (int, float)):
            return float(raw)
        try:
            return float(str(raw).strip())
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _normalize_date(raw: object) -> date | None:
        if raw is None:
            return None
        if isinstance(raw, date) and not isinstance(raw, datetime):
            return raw
        if isinstance(raw, datetime):
            return raw.date()
        if isinstance(raw, str):
            try:
                return date.fromisoformat(raw)
            except ValueError:
                return None
        return None

    @staticmethod
    def _normalize_datetime(raw: object) -> datetime | None:
        if raw is None:
            return None
        if isinstance(raw, datetime):
            return raw
        if isinstance(raw, date):
            return datetime.combine(raw, datetime.min.time())
        if isinstance(raw, str):
            text = raw.strip()
            # Try strict ISO first.
            try:
                return datetime.fromisoformat(text)
            except ValueError:
                pass
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(text, fmt)
                except ValueError:
                    continue
        return None

    def _parse_ratings(self, raw: object) -> RatingBreakdown | None:
        if raw is None or not isinstance(raw, Mapping):
            return None
        return RatingBreakdown(
            overall=self._as_float(raw.get("overall")),
            athleticism=self._as_float(raw.get("athleticism")),
            technical=self._as_float(raw.get("technical")),
            intangibles=self._as_float(raw.get("intangibles")),
            potential=self._as_float(raw.get("potential")),
        )

    def _parse_stats(self, raw: object) -> dict[str, float] | None:
        if raw is None or not isinstance(raw, Mapping):
            return None
        stats: dict[str, float] = {}
        for key, value in raw.items():
            if key is None:
                continue
            key_text = str(key)
            number = self._as_float(value)
            if number is None:
                continue
            stats[key_text] = number
        return stats or None

    def _read_parquet(self, *, name: str) -> Any:
        path = self._path_for(name)
        if not path.exists():
            raise NotFoundError(f"Parquet table {name} not found at {path}")

        try:
            import polars as pl
        except ImportError as exc:  # pragma: no cover - optional dependency at runtime
            raise MissingDependencyError("polars is required to load Parquet datasets") from exc

        try:
            return pl.read_parquet(path)
        except Exception as exc:  # pragma: no cover - surface IO errors
            raise DataValidationError(f"Failed to read Parquet table {name}: {exc}") from exc

    def _load_entity_table(self, name: str) -> list[EntitySummary]:
        if name in self._entity_cache:
            return self._entity_cache[name]

        df = self._read_parquet(name=name)
        columns = set(getattr(df, "columns", ()))
        schema = self._schema_for(name)
        required_columns = set(schema.fields) if schema else {"id", "name"}
        missing_required = required_columns.difference(columns)
        if missing_required:
            raise DataValidationError(
                f"Table {name} is missing required columns: {', '.join(sorted(missing_required))}"
            )

        records: list[EntitySummary] = []
        for row in df.to_dicts():
            entity_type = self._normalize_text(row.get("entity_type")) or name.rstrip("s")
            era = self._normalize_text(row.get("era"))
            team = self._normalize_text(row.get("team"))
            position = self._normalize_text(row.get("position"))
            logo_url = self._normalize_text(row.get("logo_url"))
            logo_path = self._normalize_text(row.get("logo_path"))
            schema_version = (
                self._normalize_text(row.get("schema_version")) or self.schema_version
            )
            source = self._normalize_text(row.get("source"))

            records.append(
                EntitySummary(
                    id=str(row["id"]),
                    name=str(row["name"]),
                    entity_type=str(entity_type),
                    era=era,
                    team=team,
                    position=position,
                    ratings=self._parse_ratings(row.get("ratings")),
                    stats=self._parse_stats(row.get("stats")),
                    schema_version=schema_version,
                    source=source,
                    updated_at=self._normalize_date(row.get("updated_at")),
                    logo_url=logo_url,
                    logo_path=logo_path,
                )
            )

        self._entity_cache[name] = records
        # Rebuild id→index map for this table (repository is single owner)
        self._rebuild_index_for_table(name, records)
        return records

    def _rebuild_index_for_table(self, name: str, records: list[EntitySummary]) -> None:
        """Rebuild id→index map when entity cache is loaded/reloaded."""
        if name == "players":
            self._players_by_id = {entity.id: idx for idx, entity in enumerate(records)}
        elif name == "teams":
            self._teams_by_id = {entity.id: idx for idx, entity in enumerate(records)}
        elif name == "coaches":
            self._coaches_by_id = {entity.id: idx for idx, entity in enumerate(records)}

    def iter_players(self) -> Iterable[EntitySummary]:
        return self._load_entity_table("players")

    def iter_teams(self) -> Iterable[EntitySummary]:
        return self._load_entity_table("teams")

    def iter_coaches(self) -> Iterable[EntitySummary]:
        return self._load_entity_table("coaches")

    def get_player_by_id(self, player_id: str) -> EntitySummary:
        """O(1) lookup by player id using index."""
        players = self._load_entity_table("players")
        idx = self._players_by_id.get(player_id)
        if idx is None:
            raise NotFoundError(f"Player {player_id} not found")
        return players[idx]

    def get_team_by_id(self, team_id: str) -> EntitySummary:
        """O(1) lookup by team id using index."""
        teams = self._load_entity_table("teams")
        idx = self._teams_by_id.get(team_id)
        if idx is None:
            raise NotFoundError(f"Team {team_id} not found")
        return teams[idx]

    def get_coach_by_id(self, coach_id: str) -> EntitySummary:
        """O(1) lookup by coach id using index."""
        coaches = self._load_entity_table("coaches")
        idx = self._coaches_by_id.get(coach_id)
        if idx is None:
            raise NotFoundError(f"Coach {coach_id} not found")
        return coaches[idx]

    def get_player(self, player_id: str) -> EntitySummary:
        """Backward compatibility wrapper for get_player_by_id."""
        return self.get_player_by_id(player_id)

    def get_team(self, team_id: str) -> EntitySummary:
        """Backward compatibility wrapper for get_team_by_id."""
        return self.get_team_by_id(team_id)

    def get_coach(self, coach_id: str) -> EntitySummary:
        """Backward compatibility wrapper for get_coach_by_id."""
        return self.get_coach_by_id(coach_id)

    def iter_games(self) -> Iterable[GameSummary]:
        if self._games_cache is not None:
            return self._games_cache

        df = self._read_parquet(name="games")
        columns = set(getattr(df, "columns", ()))
        schema = self._schema_for("games")
        required = set(schema.fields) if schema else {
            "id",
            "season",
            "week",
            "home_team",
            "away_team",
            "start_time",
            "status",
        }
        missing = required.difference(columns)
        if missing:
            raise DataValidationError(
                f"Table games is missing required columns: {', '.join(sorted(missing))}"
            )

        games: list[GameSummary] = []
        for row in df.to_dicts():
            start_time = self._normalize_datetime(row.get("start_time"))
            if start_time is None:
                raise DataValidationError(f"Invalid start_time for game {row.get('id')}")

            season = self._as_int(row.get("season"))
            week = self._as_int(row.get("week"))
            if season is None or week is None:
                raise DataValidationError(f"Invalid season/week for game {row.get('id')}")

            games.append(
                GameSummary(
                    id=str(row["id"]),
                    season=season,
                    week=week,
                    home_team=str(row["home_team"]),
                    away_team=str(row["away_team"]),
                    location=str(row.get("location") or ""),
                    start_time=start_time,
                    status=str(row.get("status") or "scheduled"),
                    is_postseason=bool(row.get("is_postseason") or False),
                    home_score=self._as_int(row.get("home_score")),
                    away_score=self._as_int(row.get("away_score")),
                    playoff_round=self._normalize_text(row.get("playoff_round")),
                )
            )

        self._games_cache = games
        return games

    def clear_cache(self) -> None:
        """Drop in-memory caches (useful for long-running UIs after data refresh)."""

        self._entity_cache.clear()
        self._games_cache = None
        self._players_by_id.clear()
        self._teams_by_id.clear()
        self._coaches_by_id.clear()

    def validate_schema(self) -> None:
        """Placeholder for schema validation logic."""

        raise NotImplementedError("Parquet schema validation is not implemented yet.")


__all__ = ["ParquetSummaryRepository", "SummaryRepository"]
