"""Schedule panel for displaying upcoming games."""

from __future__ import annotations

from typing import Iterable, Mapping
from datetime import datetime, timedelta

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gridironlabs.core.models import GameSummary, EntitySummary
from gridironlabs.ui.widgets.base_components import PanelCard


class GameRow(QFrame):
    """Individual game row showing matchup details."""

    def __init__(
        self,
        game: GameSummary,
        team_lookup: Mapping[str, EntitySummary] | None = None,
        *,
        on_team_click: callable | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("GameRow")
        self.setStyleSheet("""
            QFrame#GameRow {
                background-color: #1a1c20;
                border-radius: 4px;
            }
        """)
        self.setFixedHeight(64)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(12)

        # Lookup teams
        home_team = team_lookup.get(game.home_team) if team_lookup else None
        away_team = team_lookup.get(game.away_team) if team_lookup else None

        team_button_style = """
            QPushButton {
                color: #e5e7eb;
                border: none;
                padding: 0;
                text-align: left;
                background-color: transparent;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #d1d5db;  /* slightly darker/lower contrast to indicate click */
            }
            QPushButton:pressed {
                color: #cbd5e1;
            }
        """

        # Left Side (Away Team per mock layout)
        # Use away_team data for the left container.
        # Note: when the lookup is missing, we may only have an abbreviation (e.g., "KC").
        # The navigation callback is expected to handle abbreviations as a fallback.
        left_team = away_team
        left_display = away_team.name if away_team else game.away_team
        left_click_target = away_team.name if away_team else game.away_team
        
        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        left_logo = QLabel()
        left_logo.setFixedSize(48, 48)
        if left_team and left_team.logo_path:
            pixmap = QPixmap(left_team.logo_path)
            if not pixmap.isNull():
                left_logo.setPixmap(
                    pixmap.scaled(
                        left_logo.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                )
        left_layout.addWidget(left_logo)

        left_button = QPushButton(left_display)
        left_button.setFlat(True)
        left_button.setCursor(Qt.PointingHandCursor)
        left_button.setStyleSheet(team_button_style)
        if on_team_click and left_click_target:
            left_button.clicked.connect(lambda _, t=left_click_target: on_team_click(t))
        left_layout.addWidget(left_button)
        left_layout.addStretch(1)
        
        layout.addWidget(left_container, 1)

        # Center: Date and Time
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(2)
        center_layout.setAlignment(Qt.AlignCenter)

        date_str = game.start_time.strftime("%m/%d")
        time_str = game.start_time.strftime("%I:%M %p").lstrip("0")
        
        date_label = QLabel(date_str)
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet("color: #9ca3af; font-size: 15px;")
        
        time_label = QLabel(time_str)
        time_label.setAlignment(Qt.AlignCenter)
        time_label.setStyleSheet("color: #9ca3af; font-size: 15px;")

        center_layout.addWidget(date_label)
        center_layout.addWidget(time_label)
        
        layout.addWidget(center_container, 0)

        # Right Side (Home Team per mock layout)
        # Use home_team data for the right container.
        right_team = home_team
        right_display = home_team.name if home_team else game.home_team
        right_click_target = home_team.name if home_team else game.home_team

        right_container = QWidget()
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        
        right_layout.addStretch(1)
        right_button = QPushButton(right_display)
        right_button.setFlat(True)
        right_button.setCursor(Qt.PointingHandCursor)
        right_button.setStyleSheet(team_button_style)
        if on_team_click and right_click_target:
            right_button.clicked.connect(lambda _, t=right_click_target: on_team_click(t))
        right_layout.addWidget(right_button)

        right_logo = QLabel()
        right_logo.setFixedSize(48, 48)
        if right_team and right_team.logo_path:
            pixmap = QPixmap(right_team.logo_path)
            if not pixmap.isNull():
                right_logo.setPixmap(
                    pixmap.scaled(
                        right_logo.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                )
        right_layout.addWidget(right_logo)

        layout.addWidget(right_container, 1)


class SchedulePanel(PanelCard):
    """Panel displaying a list of upcoming or recent games with navigation."""

    def __init__(
        self, title: str = "League Schedule", *, on_team_click: callable | None = None
    ) -> None:
        super().__init__(
            title=title,
            margins=(12, 12, 12, 12),
            spacing=10,
            show_separator=True,
        )
        self._on_team_click = on_team_click

        # Navigation Header
        nav_header = QWidget()
        nav_header.setFixedHeight(32)
        nav_layout = QHBoxLayout(nav_header)
        nav_layout.setContentsMargins(4, 0, 4, 0)
        nav_layout.setSpacing(12)

        # Left: Week Nav
        self.prev_btn = QPushButton("←")
        self.prev_btn.setFixedSize(24, 24)
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.setStyleSheet("background: transparent; color: #9ca3af; font-weight: bold; border: none;")
        self.prev_btn.clicked.connect(self._prev_week)

        self.week_label = QLabel("Week 1")
        self.week_label.setObjectName("CardTitleSection")
        self.week_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #e5e7eb;")

        self.next_btn = QPushButton("→")
        self.next_btn.setFixedSize(24, 24)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setStyleSheet("background: transparent; color: #9ca3af; font-weight: bold; border: none;")
        self.next_btn.clicked.connect(self._next_week)

        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.week_label)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addStretch(1)

        # Right: Date Range
        self.date_range_label = QLabel("")
        self.date_range_label.setObjectName("CardTitleSection")
        self.date_range_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #e5e7eb;")
        nav_layout.addWidget(self.date_range_label)

        self.body_layout.addWidget(nav_header)

        # Scroll Area for Games
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.content_container = QWidget()
        self.content_container.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(12)
        self.content_layout.addStretch(1)

        self.scroll_area.setWidget(self.content_container)
        self.body_layout.addWidget(self.scroll_area)

        # State
        self._all_games: list[GameSummary] = []
        self._team_lookup: dict[str, EntitySummary] = {}
        self._current_week: int = 1
        self._max_week: int = 18
        self._season: int | None = None

    def set_data(self, games: Iterable[GameSummary], teams: Iterable[EntitySummary]) -> None:
        """Load games and teams, then render the current week."""
        self._all_games = sorted(list(games), key=lambda g: g.start_time)
        self._team_lookup = {t.team: t for t in teams if t.team}
        
        if not self._all_games:
            self.week_label.setText("No Games")
            return

        self._season = max(g.season for g in self._all_games)
        season_games = [g for g in self._all_games if g.season == self._season]
        
        if season_games:
            self._max_week = max(g.week for g in season_games)
            # Default to the first upcoming week relative to today
            now = datetime.now()
            upcoming = [g.week for g in season_games if g.start_time >= now]
            self._current_week = min(upcoming) if upcoming else self._max_week
        
        self._render_week()

    def _prev_week(self) -> None:
        if self._current_week > 1:
            self._current_week -= 1
            self._render_week()

    def _next_week(self) -> None:
        if self._current_week < self._max_week:
            self._current_week += 1
            self._render_week()

    def _render_week(self) -> None:
        # Clear content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if w := item.widget():
                w.setParent(None)

        if not self._all_games or self._season is None:
            return

        week_games = [
            g for g in self._all_games 
            if g.season == self._season and g.week == self._current_week
        ]
        
        if not week_games:
            self.week_label.setText(f"Week {self._current_week}")
            self.date_range_label.setText("")
            self.content_layout.addStretch(1)
            return

        # Update Header
        self.week_label.setText(f"Week {self._current_week}")
        
        start_date = min(g.start_time for g in week_games)
        end_date = max(g.start_time for g in week_games)
        date_fmt = "%b %d"
        if start_date.month == end_date.month:
            date_range = f"{start_date.strftime('%b')} {start_date.day}-{end_date.day}"
        else:
            date_range = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d')}"
        self.date_range_label.setText(date_range)

        # Render Games
        for game in week_games:
            row = GameRow(game, self._team_lookup, on_team_click=self._on_team_click)
            self.content_layout.addWidget(row)

        self.content_layout.addStretch(1)
