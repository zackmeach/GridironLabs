"""League leaders panel with grid-based stat cards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from gridironlabs.core.models import EntitySummary
from gridironlabs.ui.widgets.base_components import Card, PanelCard


@dataclass(frozen=True)
class LeaderEntry:
    name: str
    value: float
    team: str | None = None


@dataclass(frozen=True)
class LeaderStat:
    label: str
    entries: Sequence[LeaderEntry]


@dataclass(frozen=True)
class LeaderGroup:
    title: str
    stats: Sequence[LeaderStat]


@dataclass(frozen=True)
class LeaderboardData:
    groups: Sequence[LeaderGroup]
    season_label: str | None = None


_CATEGORY_DEFINITIONS: Sequence[tuple[str, Sequence[tuple[str, str, bool]]]] = (
    (
        "Passing",
        (
            ("Yards", "passing_yards", False),
            ("Touchdowns", "passing_tds", False),
            ("Turnovers", "interceptions", False),
        ),
    ),
    (
        "Receiving",
        (
            ("Receptions", "receptions", False),
            ("Yards", "receiving_yards", False),
            ("Touchdowns", "receiving_tds", False),
        ),
    ),
    (
        "Defense",
        (
            ("Tackles", "tackles", False),
            ("Tackles For Loss", "tackles_for_loss", False),
            ("Sacks", "sacks", False),
            ("Forced Fumbles", "forced_fumbles", False),
            ("Interceptions", "def_interceptions", False),
        ),
    ),
    (
        "Rushing",
        (
            ("Yards", "rushing_yards", False),
            ("Touchdowns", "rushing_tds", False),
        ),
    ),
    (
        "Kicking & Punting",
        (
            ("FGs Made", "field_goals_made", False),
            ("Punt Yards", "punt_yards", False),
        ),
    ),
)


def build_leaderboard(players: Iterable[EntitySummary], *, limit: int = 2) -> LeaderboardData:
    """Return grouped league leaders for the latest season in the dataset."""
    players_list = list(players)
    latest_season = _latest_numeric_season(players_list)
    season_filtered = (
        [p for p in players_list if _as_int(p.era) == latest_season] if latest_season else players_list
    )
    population = season_filtered or players_list

    groups: list[LeaderGroup] = []
    for group_title, stat_defs in _CATEGORY_DEFINITIONS:
        stat_cards: list[LeaderStat] = []
        for label, key, ascending in stat_defs:
            leaders = _top_players(population, key, limit=limit, ascending=ascending)
            if leaders:
                stat_cards.append(LeaderStat(label=label, entries=tuple(leaders)))
        if stat_cards:
            groups.append(LeaderGroup(title=group_title, stats=tuple(stat_cards)))

    season_label = f"Season {latest_season}" if latest_season else None
    return LeaderboardData(groups=tuple(groups), season_label=season_label)


def _top_players(
    players: Iterable[EntitySummary],
    stat_key: str,
    *,
    limit: int,
    ascending: bool = False,
) -> list[LeaderEntry]:
    ranked: list[tuple[float, EntitySummary]] = []
    for player in players:
        value = _extract_numeric(player.stats, stat_key)
        if value is None:
            continue
        ranked.append((value, player))
    ranked.sort(key=lambda item: item[0], reverse=not ascending)
    leaders: list[LeaderEntry] = []
    for value, player in ranked[:limit]:
        leaders.append(LeaderEntry(name=player.name, value=value, team=player.team))
    return leaders


def _extract_numeric(stats: Mapping[str, float] | None, key: str) -> float | None:
    if not stats or key not in stats:
        return None
    raw = stats.get(key)
    try:
        value = float(raw) if raw is not None else None
    except (TypeError, ValueError):
        return None
    if value is None:
        return None
    return value


def _as_int(text: str | None) -> int | None:
    if text is None:
        return None
    try:
        return int(str(text))
    except (TypeError, ValueError):
        return None


def _latest_numeric_season(players: Sequence[EntitySummary]) -> int | None:
    seasons: list[int] = []
    for player in players:
        era_int = _as_int(player.era)
        if era_int is not None:
            seasons.append(era_int)
    return max(seasons) if seasons else None


class LeaderCard(Card):
    """Small card showing the top two entries for a stat."""

    def __init__(
        self, 
        title: str, 
        entries: Sequence[LeaderEntry],
        on_player_click: Callable[[str], None] | None = None
    ) -> None:
        super().__init__(
            title=title,
            role="sub",
            margins=(12, 10, 12, 10),
            spacing=8,
            show_separator=False,
            title_object_name="CardTitleSub",
        )
        self.setStyleSheet("""
            QWidget { 
                background-color: #1a1c20; 
                border-radius: 4px;
            }
            QLabel#CardTitleSub {
                color: #e5e7eb;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        layout = self.body_layout
        
        # Grid for entries - 2 columns for side-by-side
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(16)
        
        for idx, entry in enumerate(entries):
            container = QWidget()
            container.setStyleSheet("background-color: transparent;")
            row_layout = QHBoxLayout(container)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(4)

            # Player Button (Rank + Name)
            player_btn = QPushButton(f"{idx+1}. {entry.name}")
            player_btn.setObjectName("LeaderPlayerButton")
            player_btn.setFlat(True)
            player_btn.setCursor(Qt.PointingHandCursor)
            player_btn.setStyleSheet("""
                QPushButton {
                    color: #e5e7eb; 
                    border: none; 
                    padding: 0; 
                    text-align: left; 
                    font-size: 15px;
                    background-color: transparent;
                }
                QPushButton:hover {
                    color: #3b82f6;
                }
            """)
            if on_player_click:
                player_btn.clicked.connect(lambda _, p=entry.name: on_player_click(p))
            row_layout.addWidget(player_btn)

            # Value Label
            value_text = self._format_value(entry.value)
            value_label = QLabel(f"({value_text})")
            value_label.setStyleSheet("color: #9ca3af; font-size: 15px; background-color: transparent;")
            row_layout.addWidget(value_label)
            row_layout.addStretch(1)

            grid.addWidget(container, 0, idx)

        layout.addLayout(grid)

    @staticmethod
    def _format_value(value: float) -> str:
        # Prefer whole numbers when close to an int; otherwise show one decimal.
        rounded = round(value)
        if abs(value - rounded) < 0.05:
            return f"{int(rounded):,}"
        if abs(value) >= 1000:
            return f"{value:,.0f}"
        return f"{value:,.1f}"


class LeaderSection(QWidget):
    """A category column (e.g., Passing) containing multiple stat cards."""

    def __init__(
        self, 
        title: str, 
        stats: Sequence[LeaderStat],
        on_player_click: Callable[[str], None] | None = None
    ) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Header Label (Passing, Receiving, etc.)
        header = QLabel(title)
        header.setObjectName("CardTitleSection")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #e5e7eb;")
        layout.addWidget(header)

        for stat in stats:
            layout.addWidget(LeaderCard(
                stat.label, 
                stat.entries, 
                on_player_click=on_player_click
            ))

        layout.addStretch(1)


class LeadersPanel(PanelCard):
    """Top-level panel that arranges stat groups into 3 columns."""

    def __init__(
        self, 
        *, 
        on_view_full: Callable[[], None] | None = None,
        on_player_click: Callable[[str], None] | None = None
    ) -> None:
        super().__init__(
            title="League Leaders",
            link_text="View Full Standings",
            on_link_click=on_view_full,
            margins=(12, 12, 12, 12),
            spacing=10,
            show_separator=True,
        )
        self.on_player_click = on_player_click

        # Content area with 3 columns
        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 8, 0, 0)
        self.content_layout.setSpacing(20)
        self.body_layout.addLayout(self.content_layout)

        self.empty_label = QLabel("No leaderboard data available.")
        self.empty_label.setObjectName("LeaderEmptyLabel")
        self.empty_label.setAlignment(Qt.AlignHCenter)
        self.body_layout.addWidget(self.empty_label)
        self.body_layout.addStretch(1)

    def set_data(self, data: LeaderboardData) -> None:
        self._clear_content()
        has_groups = bool(data.groups)
        self.empty_label.setVisible(not has_groups)
        
        # Standardized title with season info appended
        title = "League Leaders"
        if data.season_label:
            title += f" • {data.season_label}"
        self.set_title(title)

        if not has_groups:
            return

        # Map groups into 3 columns
        # Col 1: Passing, Rushing
        # Col 2: Receiving, Kicking & Punting
        # Col 3: Defense
        column_groups: list[list[LeaderGroup]] = [[], [], []]
        
        for group in data.groups:
            if group.title in ("Passing", "Rushing"):
                column_groups[0].append(group)
            elif group.title in ("Receiving", "Kicking & Punting"):
                column_groups[1].append(group)
            elif group.title == "Defense":
                column_groups[2].append(group)
            else:
                # Distribution logic for any extra categories
                shortest_col = min(range(3), key=lambda i: len(column_groups[i]))
                column_groups[shortest_col].append(group)

        for col_idx in range(3):
            col_container = QWidget()
            col_layout = QVBoxLayout(col_container)
            col_layout.setContentsMargins(0, 0, 0, 0)
            col_layout.setSpacing(24) # Space between categories in a column
            
            for group in column_groups[col_idx]:
                section = LeaderSection(
                    group.title, 
                    group.stats, 
                    on_player_click=self.on_player_click
                )
                col_layout.addWidget(section)
            
            col_layout.addStretch(1)
            self.content_layout.addWidget(col_container, 1)

    def _clear_content(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if widget := item.widget():
                widget.setParent(None)
