"""In-memory search scaffold for entity summaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from gridironlabs.core.models import EntitySummary, SearchResult
from gridironlabs.data.repository import SummaryRepository


@dataclass
class SearchIndex:
    players: Sequence[EntitySummary]
    teams: Sequence[EntitySummary]
    coaches: Sequence[EntitySummary]


class SearchService:
    """Placeholder search service ready for future ranking upgrades."""

    def __init__(self, repository: SummaryRepository) -> None:
        self.repository = repository
        self.index: SearchIndex | None = None

    def build_index(self) -> None:
        self.index = SearchIndex(
            players=list(self.repository.iter_players()),
            teams=list(self.repository.iter_teams()),
            coaches=list(self.repository.iter_coaches()),
        )

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        if not query:
            return []
        if self.index is None:
            self.build_index()
        lowered = query.lower()
        results: list[SearchResult] = []
        for collection in (self.index.players, self.index.teams, self.index.coaches):
            for entity in collection:
                if lowered in entity.name.lower():
                    results.append(
                        SearchResult(
                            id=entity.id,
                            label=entity.name,
                            entity_type=entity.entity_type,
                            score=None,
                            context={"team": entity.team or "", "position": entity.position or ""},
                        )
                    )
                if len(results) >= limit:
                    return results
        return results
