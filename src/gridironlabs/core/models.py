"""Domain models shared across services and data layers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Mapping, Sequence


@dataclass(frozen=True)
class RatingBreakdown:
    overall: float | None = None
    athleticism: float | None = None
    technical: float | None = None
    intangibles: float | None = None
    potential: float | None = None


@dataclass(frozen=True)
class EntitySummary:
    id: str
    name: str
    entity_type: str  # "player" | "team" | "coach"
    era: str | None = None
    team: str | None = None
    position: str | None = None
    ratings: RatingBreakdown | None = None
    stats: Mapping[str, float] | None = None
    schema_version: str | None = None
    source: str | None = None
    updated_at: date | None = None


@dataclass(frozen=True)
class ComparisonView:
    """Captures a set of summaries to visualize side-by-side."""

    entities: Sequence[EntitySummary]
    metric_keys: Sequence[str]
    advanced_metrics_enabled: bool


@dataclass(frozen=True)
class SearchResult:
    """Represents a lightweight search hit for navigation."""

    id: str
    label: str
    entity_type: str
    score: float | None = None
    context: Mapping[str, str] | None = None
