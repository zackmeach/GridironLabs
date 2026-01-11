"""Navigation service for entity-aware routing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from gridironlabs.core.errors import NotFoundError
from gridironlabs.core.models import EntityRef, Route, route_to_string

if TYPE_CHECKING:
    from PySide6.QtWidgets import QStackedWidget, QWidget

    from gridironlabs.core.models import EntitySummary
    from gridironlabs.services.summary import SummaryService


# Single source of truth: semantic Route.page → UI page widget key
ROUTE_TO_PAGE_KEY = {
    "home": "home",
    "player": "player-summary",
    "team": "team-summary",
    "coach": "coach-summary",
    "search": "search",
    "settings": "settings",
    # Section pages (legacy, use semantic names)
    "seasons": "seasons",
    "teams": "teams",
    "players": "players",
    "drafts": "drafts",
    "history": "history",
}


class NavigationService:
    """Handles entity-aware navigation and page routing.
    
    NavigationService is the only place allowed to translate Route.page → UI page key.
    All callers use semantic Route.page values.
    """

    def __init__(
        self,
        *,
        content_stack: QStackedWidget,
        pages: dict[str, QWidget],
        summary_service: SummaryService | None = None,
        logger: Any | None = None,
    ) -> None:
        self.content_stack = content_stack
        self.pages = pages
        self.summary_service = summary_service
        self.logger = logger

    def navigate(self, route: Route, *, from_history: bool = False) -> None:
        """Navigate to the given route.
        
        Args:
            route: The navigation route (typed).
            from_history: True if navigating via back/forward (skip history push).
        """
        if self.logger:
            self.logger.info("Navigate", extra={"route": route_to_string(route), "from_history": from_history})

        # Map semantic page to actual widget key
        page_key = ROUTE_TO_PAGE_KEY.get(route.page)
        if page_key is None:
            if self.logger:
                self.logger.warning("Unknown route page", extra={"page": route.page})
            return

        # Get the page widget
        page_widget = self.pages.get(page_key)
        if page_widget is None:
            if self.logger:
                self.logger.warning("Page widget not found", extra={"page_key": page_key})
            return

        # Show the page first
        self.content_stack.setCurrentWidget(page_widget)
        
        # For entity pages, resolve the entity and call set_route
        if route.entity:
            summary = self._resolve_entity(route.entity)
            if hasattr(page_widget, "set_route"):
                page_widget.set_route(route, summary)

    def _resolve_entity(self, entity_ref: EntityRef) -> EntitySummary | None:
        """Resolve EntityRef to EntitySummary via SummaryService.
        
        Returns None if entity not found (page will render NotFoundPanel).
        """
        if self.summary_service is None:
            if self.logger:
                self.logger.warning("SummaryService not available", extra={"entity_ref": str(entity_ref)})
            return None
        
        try:
            if entity_ref.entity_type == "player":
                return self.summary_service.get_player_by_id(entity_ref.id)
            elif entity_ref.entity_type == "team":
                return self.summary_service.get_team_by_id(entity_ref.id)
            elif entity_ref.entity_type == "coach":
                return self.summary_service.get_coach_by_id(entity_ref.id)
            else:
                if self.logger:
                    self.logger.warning("Unknown entity type", extra={"entity_type": entity_ref.entity_type})
                return None
        except NotFoundError as exc:
            if self.logger:
                self.logger.warning("Entity not found", extra={"entity_ref": str(entity_ref), "error": str(exc)})
            return None


__all__ = ["NavigationService", "ROUTE_TO_PAGE_KEY"]
