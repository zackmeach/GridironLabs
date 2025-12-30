"""Team summary page implementation."""

from __future__ import annotations

from gridironlabs.ui.pages.base_page import BasePage
from gridironlabs.ui.style.tokens import GRID

class TeamSummaryPage(BasePage):
    """A barebones team summary page."""

    def __init__(self, title: str = "Team Summary", subtitle: str = "Detailed team overview") -> None:
        super().__init__(cols=GRID.cols, rows=12)
        self.setObjectName("page-team-summary")
        self._team_name: str | None = None

    def set_team(self, team_name: str) -> None:
        """Update the page content for a specific team."""
        self._team_name = team_name

