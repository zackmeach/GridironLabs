"""Player summary page implementation."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from gridironlabs.core.models import EntitySummary, Route
from gridironlabs.ui.pages.base_page import BasePage
from gridironlabs.ui.panels import PanelChrome
from gridironlabs.ui.style.tokens import GRID
from gridironlabs.ui.widgets.key_value_list import KeyValueList


class NotFoundPanel(PanelChrome):
    """Standard not-found panel for missing entities."""

    def __init__(self, entity_type: str, entity_id: str) -> None:
        super().__init__(title="NOT FOUND", panel_variant="card")
        
        message = QLabel(f"{entity_type.title()} with ID '{entity_id}' not found.")
        message.setObjectName("NotFoundMessage")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        
        self.set_body(message)


class PlayerSummaryPage(BasePage):
    """Player summary page with PERSONAL DETAILS panel."""

    def __init__(self) -> None:
        super().__init__(cols=GRID.cols, rows=12)
        self.setObjectName("page-player-summary")
        self._current_panel: PanelChrome | None = None

    def set_route(self, route: Route, summary: EntitySummary | None) -> None:
        """Render the page for the given route.
        
        Args:
            route: The navigation route that triggered this page.
            summary: The resolved entity data, or None if not found.
        
        If summary is None, render the shared NotFoundPanel.
        Otherwise, render the entity's detail panels.
        """
        # Clear existing panel
        if self._current_panel:
            self.remove_panel(self._current_panel)
            self._current_panel = None

        if summary is None:
            # Render NotFoundPanel
            entity_id = route.entity.id if route.entity else "unknown"
            panel = NotFoundPanel(entity_type="player", entity_id=entity_id)
            self.add_panel(panel, col=0, row=0, col_span=GRID.cols, row_span=6)
            self._current_panel = panel
        else:
            # Render PERSONAL DETAILS panel
            panel = self._build_personal_details_panel(summary)
            self.add_panel(panel, col=0, row=0, col_span=18, row_span=12)
            self._current_panel = panel

    def _build_personal_details_panel(self, player: EntitySummary) -> PanelChrome:
        """Build the PERSONAL DETAILS panel from EntitySummary."""
        panel = PanelChrome(title="PERSONAL DETAILS", panel_variant="table")
        
        kv_list = KeyValueList(key_width=190)
        
        # ID (for debugging during rollout; kept until Phase 4)
        kv_list.add_row(key="ID", value=player.id)
        
        # Name
        kv_list.add_row(key="Name", value=player.name)
        
        # Position
        kv_list.add_row(key="Position", value=player.position or "—")
        
        # Team (abbr)
        kv_list.add_row(key="Team", value=player.team or "—")
        
        # Era
        kv_list.add_row(key="Era", value=player.era or "—")
        
        # Schema version
        kv_list.add_row(key="Schema Version", value=player.schema_version or "—")
        
        # Source
        kv_list.add_row(key="Source", value=player.source or "—")
        
        # Updated at (formatted)
        if player.updated_at:
            updated_str = player.updated_at.isoformat()
        else:
            updated_str = "—"
        kv_list.add_row(key="Updated At", value=updated_str)
        
        panel.set_body(kv_list)
        return panel

