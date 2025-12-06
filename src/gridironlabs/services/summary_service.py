from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from gridironlabs.core.models import CoachSummary, PlayerSummary, TeamSummary
from gridironlabs.core.repository import SummaryRepository


@dataclass
class SummaryService:
    """Domain-facing orchestrator to fetch and prepare summary payloads."""

    repository: SummaryRepository

    def player(self, player_id: str) -> Optional[PlayerSummary]:
        return next((p for p in self.repository.players() if p.player_id == player_id), None)

    def team(self, team_id: str) -> Optional[TeamSummary]:
        return next((t for t in self.repository.teams() if t.team_id == team_id), None)

    def coach(self, coach_id: str) -> Optional[CoachSummary]:
        return next((c for c in self.repository.coaches() if c.coach_id == coach_id), None)
