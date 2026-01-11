"""Tests for entity-aware navigation (Route + NavigationService)."""

from __future__ import annotations

from datetime import date
from typing import Iterable

import pytest
from PySide6.QtWidgets import QApplication

from gridironlabs.core.errors import NotFoundError
from gridironlabs.core.models import EntityRef, EntitySummary, GameSummary, RatingBreakdown, Route
from gridironlabs.data.repository import SummaryRepository
from gridironlabs.services.summary import SummaryService
from gridironlabs.ui.navigation_service import NavigationService
from gridironlabs.ui.pages.player_page import PlayerSummaryPage


class FakeRepository(SummaryRepository):
    """Lightweight fake repository with deterministic test data."""

    def __init__(self) -> None:
        # One player, one team, one coach for testing
        self._players = [
            EntitySummary(
                id="player-test-001",
                name="Test Player",
                entity_type="player",
                era="2025",
                team="KC",
                position="QB",
                ratings=RatingBreakdown(overall=85.0, athleticism=80.0, technical=88.0),
                stats={"passing_yards": 4500.0, "passing_tds": 35.0},
                schema_version="v0",
                source="test",
                updated_at=date(2025, 1, 1),
            )
        ]
        self._teams = [
            EntitySummary(
                id="team-test-001",
                name="Kansas City Chiefs",
                entity_type="team",
                era="2025",
                team="KC",
                ratings=RatingBreakdown(overall=90.0),
                stats={"wins": 12.0, "losses": 5.0},
                schema_version="v0",
                source="test",
                updated_at=date(2025, 1, 1),
            )
        ]
        self._coaches = [
            EntitySummary(
                id="coach-test-001",
                name="Test Coach",
                entity_type="coach",
                era="2025",
                team="KC",
                ratings=RatingBreakdown(overall=88.0),
                stats={"wins": 12.0, "losses": 5.0},
                schema_version="v0",
                source="test",
                updated_at=date(2025, 1, 1),
            )
        ]

    def iter_players(self) -> Iterable[EntitySummary]:
        return self._players

    def iter_teams(self) -> Iterable[EntitySummary]:
        return self._teams

    def iter_coaches(self) -> Iterable[EntitySummary]:
        return self._coaches

    def iter_games(self) -> Iterable[GameSummary]:
        return []

    def get_player_by_id(self, player_id: str) -> EntitySummary:
        for p in self._players:
            if p.id == player_id:
                return p
        raise NotFoundError(f"Player {player_id} not found")

    def get_team_by_id(self, team_id: str) -> EntitySummary:
        for t in self._teams:
            if t.id == team_id:
                return t
        raise NotFoundError(f"Team {team_id} not found")

    def get_coach_by_id(self, coach_id: str) -> EntitySummary:
        for c in self._coaches:
            if c.id == coach_id:
                return c
        raise NotFoundError(f"Coach {coach_id} not found")

    def get_player(self, player_id: str) -> EntitySummary:
        return self.get_player_by_id(player_id)

    def get_team(self, team_id: str) -> EntitySummary:
        return self.get_team_by_id(team_id)

    def get_coach(self, coach_id: str) -> EntitySummary:
        return self.get_coach_by_id(coach_id)


@pytest.fixture
def fake_repo() -> FakeRepository:
    """Provide a fake repository with test data."""
    return FakeRepository()


@pytest.fixture
def summary_service(fake_repo: FakeRepository) -> SummaryService:
    """Provide a summary service backed by fake repository."""
    return SummaryService(repository=fake_repo)


def test_entity_ref_creation() -> None:
    """Test EntityRef can be created with required fields."""
    ref = EntityRef(entity_type="player", id="player-test-001")
    assert ref.entity_type == "player"
    assert ref.id == "player-test-001"
    assert ref.season is None


def test_entity_ref_with_season() -> None:
    """Test EntityRef can include optional season."""
    ref = EntityRef(entity_type="player", id="player-test-001", season=2025)
    assert ref.season == 2025


def test_route_creation() -> None:
    """Test Route can be created with semantic page values."""
    route = Route(page="home")
    assert route.page == "home"
    assert route.entity is None


def test_route_with_entity() -> None:
    """Test Route can include entity reference."""
    entity_ref = EntityRef(entity_type="player", id="player-test-001")
    route = Route(page="player", entity=entity_ref)
    assert route.page == "player"
    assert route.entity == entity_ref


def test_fake_repo_get_player_by_id(fake_repo: FakeRepository) -> None:
    """Test FakeRepository returns player by ID."""
    player = fake_repo.get_player_by_id("player-test-001")
    assert player.id == "player-test-001"
    assert player.name == "Test Player"
    assert player.entity_type == "player"


def test_fake_repo_player_not_found(fake_repo: FakeRepository) -> None:
    """Test FakeRepository raises NotFoundError for missing player."""
    with pytest.raises(NotFoundError, match="Player missing-id not found"):
        fake_repo.get_player_by_id("missing-id")


def test_summary_service_get_player_by_id(summary_service: SummaryService) -> None:
    """Test SummaryService resolves player by ID."""
    player = summary_service.get_player_by_id("player-test-001")
    assert player.id == "player-test-001"
    assert player.name == "Test Player"


def test_player_summary_page_set_route_with_summary(qtbot) -> None:  # noqa: ANN001
    """Test PlayerSummaryPage renders PERSONAL DETAILS when summary is provided."""
    page = PlayerSummaryPage()
    qtbot.addWidget(page)
    
    # Create a test player
    player = EntitySummary(
        id="player-test-002",
        name="Another Player",
        entity_type="player",
        era="2025",
        team="SF",
        position="WR",
        schema_version="v0",
        source="test",
        updated_at=date(2025, 1, 1),
    )
    
    # Create route
    route = Route(page="player", entity=EntityRef(entity_type="player", id="player-test-002"))
    
    # Call set_route
    page.set_route(route, player)
    
    # Verify panel was added
    assert page._current_panel is not None
    assert page._current_panel.header_primary.title_label.text() == "PERSONAL DETAILS"


def test_player_summary_page_set_route_not_found(qtbot) -> None:  # noqa: ANN001
    """Test PlayerSummaryPage renders NotFoundPanel when summary is None."""
    page = PlayerSummaryPage()
    qtbot.addWidget(page)
    
    # Create route with missing player
    route = Route(page="player", entity=EntityRef(entity_type="player", id="missing-player"))
    
    # Call set_route with None summary
    page.set_route(route, None)
    
    # Verify NotFoundPanel was added
    assert page._current_panel is not None
    assert page._current_panel.header_primary.title_label.text() == "NOT FOUND"


def test_navigation_service_navigate_to_player(qtbot, summary_service: SummaryService) -> None:  # noqa: ANN001
    """Test NavigationService navigates to player and calls set_route."""
    from PySide6.QtWidgets import QStackedWidget
    
    # Create minimal page setup
    player_page = PlayerSummaryPage()
    qtbot.addWidget(player_page)
    
    stack = QStackedWidget()
    qtbot.addWidget(stack)
    stack.addWidget(player_page)
    
    pages = {"player-summary": player_page}
    
    nav_service = NavigationService(
        content_stack=stack,
        pages=pages,
        summary_service=summary_service,
        logger=None,
    )
    
    # Navigate to player
    route = Route(page="player", entity=EntityRef(entity_type="player", id="player-test-001"))
    nav_service.navigate(route)
    
    # Verify page was shown
    assert stack.currentWidget() == player_page
    
    # Verify set_route was called (panel should exist)
    assert player_page._current_panel is not None


def test_navigation_service_navigate_to_missing_player(qtbot, summary_service: SummaryService) -> None:  # noqa: ANN001
    """Test NavigationService handles missing player gracefully."""
    from PySide6.QtWidgets import QStackedWidget
    
    player_page = PlayerSummaryPage()
    qtbot.addWidget(player_page)
    
    stack = QStackedWidget()
    qtbot.addWidget(stack)
    stack.addWidget(player_page)
    
    pages = {"player-summary": player_page}
    
    nav_service = NavigationService(
        content_stack=stack,
        pages=pages,
        summary_service=summary_service,
        logger=None,
    )
    
    # Navigate to missing player
    route = Route(page="player", entity=EntityRef(entity_type="player", id="missing-player"))
    nav_service.navigate(route)
    
    # Verify page was shown with NotFoundPanel
    assert stack.currentWidget() == player_page
    assert player_page._current_panel is not None
    assert player_page._current_panel.header_primary.title_label.text() == "NOT FOUND"
