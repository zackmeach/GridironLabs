from __future__ import annotations

"""
Parquet-backed repository that feeds the UI from generated/ingested datasets.

This lets the UI operate on the synthetic-but-complete datasets produced by
`scripts/generate_fake_nfl_data.py` without waiting for real pipelines.
"""

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

from gridironlabs.core.models import CoachSummary, PlayerSummary, TeamSummary
from gridironlabs.core.repository import SummaryRepository
from gridironlabs.data.loaders.parquet_loader import has_parquet, load_parquet_table


def _coerce_date(value: object) -> Optional[date]:
    """Convert pandas/str dates to `date`, otherwise None."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def _coerce_dict(value: object) -> dict:
    """Best-effort conversion to dict for nested rating/stats fields."""
    if isinstance(value, dict):
        return value
    return {}


def _coerce_list(value: object) -> list:
    if isinstance(value, list):
        return value
    return []


@dataclass
class ParquetSummaryRepository(SummaryRepository):
    """
    Lightweight in-memory cache sourced from Parquet outputs.
    """

    players_path: str
    teams_path: str
    coaches_path: str

    def __post_init__(self) -> None:
        self._players = self._load_players()
        self._teams = self._load_teams()
        self._coaches = self._load_coaches()

    # SummaryRepository API -------------------------------------------------
    def players(self) -> Iterable[PlayerSummary]:
        return self._players

    def teams(self) -> Iterable[TeamSummary]:
        return self._teams

    def coaches(self) -> Iterable[CoachSummary]:
        return self._coaches

    # Load helpers ---------------------------------------------------------
    def _load_players(self) -> tuple[PlayerSummary, ...]:
        df = load_parquet_table(Path(self.players_path))
        records = df.to_dict(orient="records")
        players: list[PlayerSummary] = []
        for row in records:
            players.append(
                PlayerSummary(
                    player_id=str(row.get("player_id") or ""),
                    name=str(row.get("name") or ""),
                    position=str(row.get("position") or ""),
                    team=(row.get("team") or None),
                    birth_date=_coerce_date(row.get("birth_date")),
                    ratings=_coerce_dict(row.get("ratings")),
                    stats=_coerce_dict(row.get("career_stats") or row.get("stats")),
                )
            )
        return tuple(players)

    def _load_teams(self) -> tuple[TeamSummary, ...]:
        df = load_parquet_table(Path(self.teams_path))
        records = df.to_dict(orient="records")
        teams: list[TeamSummary] = []
        for row in records:
            teams.append(
                TeamSummary(
                    team_id=str(row.get("team_id") or ""),
                    name=str(row.get("name") or ""),
                    conference=row.get("conference") or None,
                    division=row.get("division") or None,
                    ratings=_coerce_dict(row.get("ratings")),
                    stats=_coerce_dict(row.get("stats")),
                )
            )
        return tuple(teams)

    def _load_coaches(self) -> tuple[CoachSummary, ...]:
        df = load_parquet_table(Path(self.coaches_path))
        records = df.to_dict(orient="records")
        coaches: list[CoachSummary] = []
        for row in records:
            coaches.append(
                CoachSummary(
                    coach_id=str(row.get("coach_id") or ""),
                    name=str(row.get("name") or ""),
                    role=str(row.get("role") or ""),
                    team=row.get("team") or None,
                    history=_coerce_list(row.get("history")),
                    ratings=_coerce_dict(row.get("ratings")),
                    stats=_coerce_dict(row.get("stats")),
                )
            )
        return tuple(coaches)

    # Availability ---------------------------------------------------------
    @classmethod
    def available(cls, players_path: str, teams_path: str, coaches_path: str) -> bool:
        return all(has_parquet(Path(p)) for p in (players_path, teams_path, coaches_path))


__all__ = ["ParquetSummaryRepository"]

