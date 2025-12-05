 from __future__ import annotations
 
from dataclasses import dataclass
from typing import List
 from gridironlabs.core.repository import SearchResult, SummaryRepository
 
 
 @dataclass
 class SimpleSearchResult:
     id: str
     name: str
     entity_type: str
     snippet: str | None = None
 
 
 class SearchService:
     """
     Minimal in-memory search over cached summaries.
     """
 
     def __init__(self, repository: SummaryRepository):
         self.repository = repository
 
     def search(self, query: str, limit: int = 25) -> List[SearchResult]:
         q = query.lower().strip()
         results: list[SimpleSearchResult] = []
 
         def match(name: str) -> bool:
             return q in name.lower()
 
         for player in self.repository.players():
             if match(player.name):
                 results.append(
                     SimpleSearchResult(
                         id=player.player_id,
                         name=player.name,
                         entity_type="player",
                         snippet=f"{player.position} | {player.team}",
                     )
                 )
         for team in self.repository.teams():
             if match(team.name):
                 results.append(
                     SimpleSearchResult(
                         id=team.team_id,
                         name=team.name,
                         entity_type="team",
                         snippet=team.division,
                     )
                 )
         for coach in self.repository.coaches():
             if match(coach.name):
                 results.append(
                     SimpleSearchResult(
                         id=coach.coach_id,
                         name=coach.name,
                         entity_type="coach",
                         snippet=coach.role,
                     )
                 )
 
         return results[:limit]
