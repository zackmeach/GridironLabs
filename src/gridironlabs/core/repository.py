from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Protocol

from .models import CoachSummary, PlayerSummary, TeamSummary


class SummaryRepository(ABC):
    """Repository facade for summary datasets."""

    @abstractmethod
    def players(self) -> Iterable[PlayerSummary]:
        raise NotImplementedError

    @abstractmethod
    def teams(self) -> Iterable[TeamSummary]:
        raise NotImplementedError

    @abstractmethod
    def coaches(self) -> Iterable[CoachSummary]:
        raise NotImplementedError


class SearchResult(Protocol):
    id: str
    name: str
    entity_type: str
