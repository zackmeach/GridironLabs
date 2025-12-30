"""Player summary page implementation."""

from __future__ import annotations

from gridironlabs.ui.pages.base_page import BasePage
from gridironlabs.ui.style.tokens import GRID

class PlayerSummaryPage(BasePage):
    """A barebones player summary page."""

    def __init__(self, title: str = "Player Summary", subtitle: str = "Detailed player overview") -> None:
        super().__init__(cols=GRID.cols, rows=12)
        self.setObjectName("page-player-summary")
        self._player_name: str | None = None

    def set_player(self, player_name: str) -> None:
        """Update the page content for a specific player."""
        self._player_name = player_name

