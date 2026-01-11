"""Domain models shared across services and data layers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Literal, Mapping, Sequence


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
    logo_url: str | None = None
    logo_path: str | None = None


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


@dataclass(frozen=True)
class GameSummary:
    """Scheduled or completed game metadata."""

    id: str
    season: int
    week: int
    home_team: str
    away_team: str
    location: str
    start_time: datetime
    status: str  # "scheduled" | "final"
    is_postseason: bool = False
    home_score: int | None = None
    away_score: int | None = None
    playoff_round: str | None = None


@dataclass(frozen=True)
class EntityRef:
    """Canonical reference to a player/team/coach entity for navigation."""

    entity_type: Literal["player", "team", "coach"]
    id: str
    season: int | None = None  # optional; future-proofing for multi-era data


@dataclass(frozen=True)
class Route:
    """Internal navigation route (typed; history stores Route instances)."""

    page: Literal["home", "player", "team", "coach", "search", "settings"]
    entity: EntityRef | None = None
    params: dict[str, Any] = field(default_factory=dict)
    ui_state: dict[str, Any] = field(default_factory=dict)


def route_to_string(route: Route) -> str:
    """Convert Route to a debug/log string (no parsing implemented in Phase 1)."""
    if route.entity:
        entity_str = f"{route.entity.entity_type}:{route.entity.id}"
        if route.entity.season:
            entity_str += f"@{route.entity.season}"
        return f"Route({route.page}, {entity_str})"
    if route.params:
        params_str = ",".join(f"{k}={v}" for k, v in route.params.items())
        return f"Route({route.page}, params={params_str})"
    return f"Route({route.page})"
