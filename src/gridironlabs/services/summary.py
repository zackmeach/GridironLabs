"""Summary retrieval service to supply UI payloads."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from gridironlabs.core.models import ComparisonView, EntitySummary
from gridironlabs.data.repository import SummaryRepository


@dataclass
class SummaryService:
    repository: SummaryRepository

    def get_player(self, player_id: str) -> EntitySummary:
        return self.repository.get_player(player_id)

    def get_team(self, team_id: str) -> EntitySummary:
        return self.repository.get_team(team_id)

    def get_coach(self, coach_id: str) -> EntitySummary:
        return self.repository.get_coach(coach_id)

    def compare(
        self, *, entity_ids: Sequence[str], advanced_metrics: bool = False
    ) -> ComparisonView:
        entities: list[EntitySummary] = []
        for entity_id in entity_ids:
            try:
                entities.append(self.get_player(entity_id))
            except Exception:
                pass
        return ComparisonView(
            entities=entities,
            metric_keys=tuple(),
            advanced_metrics_enabled=advanced_metrics,
        )
