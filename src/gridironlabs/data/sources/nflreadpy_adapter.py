"""Adapter for sourcing data from nflreadpy with graceful fallbacks."""

from __future__ import annotations

from typing import Iterable

from gridironlabs.core.errors import MissingDependencyError
from gridironlabs.core.models import EntitySummary


class NFLReadPyAdapter:
    """Placeholder adapter to wrap nflreadpy usage."""

    def __init__(self, *, enabled: bool) -> None:
        self.enabled = enabled

    def fetch_players(self) -> Iterable[EntitySummary]:
        if not self.enabled:
            return []
        try:
            import nflreadpy  # type: ignore  # pragma: no cover
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise MissingDependencyError("nflreadpy is not installed") from exc
        _ = nflreadpy  # Prevent unused-import linting until integration lands.
        raise NotImplementedError("nflreadpy integration will be implemented later.")

    def fetch_teams(self) -> Iterable[EntitySummary]:
        if not self.enabled:
            return []
        raise NotImplementedError

    def fetch_coaches(self) -> Iterable[EntitySummary]:
        if not self.enabled:
            return []
        raise NotImplementedError
