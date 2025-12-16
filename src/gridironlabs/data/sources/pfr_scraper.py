"""Scraping adapter for Pro-Football-Reference with cautious defaults."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from gridironlabs.core.errors import MissingDependencyError
from gridironlabs.core.models import EntitySummary


@dataclass(frozen=True)
class ScrapeConfig:
    user_agent: str = "GridironLabs/0.1 (+https://gridironlabs.local)"
    timeout_seconds: float = 5.0
    max_retries: int = 2
    backoff_seconds: float = 0.5
    cache_dir: str = ".cache/pfr"


class PfrScraper:
    """Placeholder for PFR scraping logic with polite defaults."""

    def __init__(self, config: ScrapeConfig, *, enabled: bool) -> None:
        self.config = config
        self.enabled = enabled

    def fetch_players(self) -> Iterable[EntitySummary]:
        if not self.enabled:
            return []
        try:
            import requests  # type: ignore  # pragma: no cover
        except ImportError as exc:  # pragma: no cover - should be present
            raise MissingDependencyError("requests is required for scraping") from exc
        _ = requests  # Prevent unused-import linting until scraping is implemented.
        raise NotImplementedError("PFR scraping will be implemented later.")

    def fetch_teams(self) -> Iterable[EntitySummary]:
        if not self.enabled:
            return []
        raise NotImplementedError("PFR team scraping will be implemented later.")

    def fetch_coaches(self) -> Iterable[EntitySummary]:
        if not self.enabled:
            return []
        raise NotImplementedError("PFR coach scraping will be implemented later.")
