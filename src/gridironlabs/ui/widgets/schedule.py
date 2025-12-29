"""Schedule panel for displaying upcoming games."""

from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from gridironlabs.core.models import GameSummary
from gridironlabs.ui.widgets.base_components import PanelCard


class SchedulePanel(PanelCard):
    """Panel displaying a list of upcoming or recent games (Skeleton)."""

    def __init__(self, title: str = "Schedule") -> None:
        super().__init__(
            title=title,
            margins=(12, 12, 12, 12),
            spacing=10,
            show_separator=True,
        )

        self.empty_label = QLabel("Schedule placeholder (performance optimization)")
        self.empty_label.setObjectName("ScheduleEmptyLabel")
        self.empty_label.setAlignment(Qt.AlignHCenter)
        self.body_layout.addWidget(self.empty_label)

    def set_games(self, games: Iterable[GameSummary]) -> None:
        """Populate the panel with game cards (Disabled)."""
        # Skeleton implementation: do nothing or just show a count
        # Avoid creating widgets to prevent startup lag
        games_list = list(games)
        self.empty_label.setText(f"Schedule placeholder ({len(games_list)} games loaded)")
