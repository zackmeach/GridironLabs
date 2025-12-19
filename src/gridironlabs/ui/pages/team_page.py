"""Team summary page implementation."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from gridironlabs.ui.pages.base_page import BasePage
from gridironlabs.ui.style.tokens import GRID

class TeamSummaryPage(BasePage):
    """A barebones team summary page."""

    def __init__(self, title: str = "Team Summary", subtitle: str = "Detailed team overview") -> None:
        super().__init__(cols=GRID.cols, rows=12)
        self.setObjectName("page-team-summary")
        
        # Placeholder content
        self.placeholder_label = QLabel(f"Summary for {title}")
        self.placeholder_label.setStyleSheet("font-size: 24px; color: white;")
        
        # We can add a simple panel to show it's working
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.addWidget(self.placeholder_label)
        layout.addStretch(1)
        
        self.add_panel(content, col=0, row=0, col_span=GRID.cols, row_span=4)

    def set_team(self, team_name: str) -> None:
        """Update the page content for a specific team."""
        self.placeholder_label.setText(f"Summary for {team_name}")
        self.setObjectName(f"page-team-{team_name.lower().replace(' ', '-')}")

