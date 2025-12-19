"""Standings panels for displaying league tables."""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from gridironlabs.ui.widgets.panel_card import PanelCard


class HomeStandingsPanel(PanelCard):
    """League standings summary panel for the home page."""

    def __init__(
        self, 
        on_view_full: Callable[[], None] | None = None,
        on_team_click: Callable[[str], None] | None = None
    ) -> None:
        super().__init__(
            title="League Standings",
            link_text="View Full Standings",
            on_link_click=on_view_full,
        )
        self.on_team_click = on_team_click

        # Main content area (Yellow in concept)
        self.content_container = QWidget()
        self.content_layout = QHBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)  # Space between conference columns
        self.body_layout.addWidget(self.content_container)

        # Left Column (AFC)
        self.afc_column = self._build_conference_column("AFC")
        self.content_layout.addWidget(self.afc_column)

        # Right Column (NFC)
        self.nfc_column = self._build_conference_column("NFC")
        self.content_layout.addWidget(self.nfc_column)

    def _build_conference_column(self, title: str) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)  # Increased spacing between division blocks

        # Conference Header (e.g., AFC)
        header_label = QLabel(title)
        header_label.setObjectName("CardTitleSection")
        header_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(header_label)

        # Division Data Mapping
        team_data = {
            "AFC": {
                "North": ["Ravens (0-0)", "Steelers (0-0)", "Browns (0-0)", "Bengals (0-0)"],
                "South": ["Texans (0-0)", "Colts (0-0)", "Jaguars (0-0)", "Titans (0-0)"],
                "East": ["Bills (0-0)", "Dolphins (0-0)", "Jets (0-0)", "Patriots (0-0)"],
                "West": ["Chiefs (0-0)", "Raiders (0-0)", "Broncos (0-0)", "Chargers (0-0)"],
            },
            "NFC": {
                "North": ["Lions (0-0)", "Packers (0-0)", "Vikings (0-0)", "Bears (0-0)"],
                "South": ["Buccaneers (0-0)", "Saints (0-0)", "Falcons (0-0)", "Panthers (0-0)"],
                "East": ["Cowboys (0-0)", "Eagles (0-0)", "Giants (0-0)", "Commanders (0-0)"],
                "West": ["49ers (0-0)", "Rams (0-0)", "Seahawks (0-0)", "Cardinals (0-0)"],
            },
        }

        conference_teams = team_data.get(title, {})
        divisions = ["North", "South", "East", "West"]

        for div in divisions:
            # Division Block (Styled like LeaderCard)
            div_block = QFrame()
            div_block.setStyleSheet("""
                QFrame {
                    background-color: #1a1c20;
                    border-radius: 4px;
                }
            """)
            div_layout = QVBoxLayout(div_block)
            div_layout.setContentsMargins(12, 10, 12, 10)
            div_layout.setSpacing(8)

            # Division Title
            div_label = QLabel(f"{title} {div}")
            div_label.setObjectName("CardTitleSub")
            div_label.setAlignment(Qt.AlignLeft)
            div_layout.addWidget(div_label)

            # Team Grid (4 columns)
            team_grid = QGridLayout()
            team_grid.setContentsMargins(0, 0, 0, 0)
            team_grid.setHorizontalSpacing(16)
            team_grid.setVerticalSpacing(4)
            
            div_teams = conference_teams.get(div, ["Team 1", "Team 2", "Team 3", "Team 4"])
            for i, team_name in enumerate(div_teams):
                rank = i + 1
                team_button = QPushButton(f"{rank}. {team_name}")
                team_button.setFlat(True)
                team_button.setCursor(Qt.PointingHandCursor)
                team_button.setStyleSheet("""
                    QPushButton {
                        color: #9ca3af; 
                        font-size: 15px; 
                        text-align: left; 
                        padding: 0; 
                        border: none;
                        background-color: transparent;
                    }
                    QPushButton:hover {
                        color: #3b82f6;
                    }
                """)
                
                if self.on_team_click:
                    pure_name = team_name.split(" (")[0]
                    team_button.clicked.connect(lambda _, t=pure_name: self.on_team_click(t))
                
                team_grid.addWidget(team_button, 0, i)
            
            # Allow columns to expand evenly
            for col in range(4):
                team_grid.setColumnStretch(col, 1)

            div_layout.addLayout(team_grid)
            layout.addWidget(div_block)
        
        layout.addStretch(1) # Push content up
        return container

