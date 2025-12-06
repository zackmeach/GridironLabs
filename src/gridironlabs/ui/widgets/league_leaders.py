"""League leaders panel with grid-based stat cards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from gridironlabs.core.models import EntitySummary


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
        "Rushing",
        (
            ("Yards", "rushing_yards", False),
            ("Touchdowns", "rushing_tds", False),
        ),
    ),
    (
        "Receiving",
        (
            ("Yards", "receiving_yards", False),
            ("Touchdowns", "receiving_tds", False),
        ),
    ),
    (
        "Defense",
        (
            ("Tackles", "tackles", False),
            ("Sacks", "sacks", False),
            ("Forced Fumbles", "forced_fumbles", False),
            ("Interceptions", "def_interceptions", False),
        ),
    ),
    (
        "Kicking & Punting",
        (
            ("FGs Made", "field_goals_made", False),
            ("Punts", "punts", False),
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


class LeaderCard(QFrame):
    """Small card showing the top two entries for a stat."""

    def __init__(self, title: str, entries: Sequence[LeaderEntry]) -> None:
        super().__init__()
        self.setObjectName("LeaderCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("LeaderCardTitle")
        layout.addWidget(title_label)

        for idx, entry in enumerate(entries, start=1):
            label = QLabel(self._format_entry(idx, entry))
            label.setObjectName("LeaderEntry")
            label.setWordWrap(True)
            layout.addWidget(label)

    def _format_entry(self, rank: int, entry: LeaderEntry) -> str:
        value_text = self._format_value(entry.value)
        team_text = f" [{entry.team}]" if entry.team else ""
        return f"{rank}. {entry.name}{team_text} ({value_text})"

    @staticmethod
    def _format_value(value: float) -> str:
        # Prefer whole numbers when close to an int; otherwise show one decimal.
        rounded = round(value)
        if abs(value - rounded) < 0.05:
            return f"{int(rounded):,}"
        if abs(value) >= 1000:
            return f"{value:,.0f}"
        return f"{value:,.1f}"


class LeaderSection(QFrame):
    """Column of stat cards within a category such as Passing or Defense."""

    def __init__(self, title: str, stats: Sequence[LeaderStat]) -> None:
        super().__init__()
        self.setObjectName("LeaderSection")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        heading = QLabel(title)
        heading.setObjectName("LeaderSectionTitle")
        layout.addWidget(heading)

        for stat in stats:
            layout.addWidget(LeaderCard(stat.label, stat.entries))

        layout.addStretch(1)


class LeadersPanel(QFrame):
    """Top-level panel that arranges stat groups on a grid."""

    def __init__(self, *, on_view_full: Callable[[], None] | None = None) -> None:
        super().__init__()
        self.setObjectName("LeadersPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(8)

        title = QLabel("League Leaders")
        title.setObjectName("LeadersTitle")
        header.addWidget(title)

        self.season_label = QLabel()
        self.season_label.setObjectName("LeadersSeasonLabel")
        self.season_label.setVisible(False)
        header.addWidget(self.season_label)
        header.addStretch(1)

        action = QPushButton("View Full Standings")
        action.setObjectName("LeadersActionButton")
        action.setFlat(True)
        action.setCursor(Qt.PointingHandCursor)
        if on_view_full:
            action.clicked.connect(on_view_full)
        else:
            action.setEnabled(False)
        header.addWidget(action, 0, Qt.AlignRight)
        layout.addLayout(header)

        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setHorizontalSpacing(10)
        self.grid.setVerticalSpacing(10)
        layout.addLayout(self.grid)

        self.empty_label = QLabel("No leaderboard data available.")
        self.empty_label.setObjectName("LeaderEmptyLabel")
        self.empty_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.empty_label)

    def set_data(self, data: LeaderboardData) -> None:
        self._clear_grid()
        has_groups = bool(data.groups)
        self.empty_label.setVisible(not has_groups)
        self.season_label.setVisible(bool(data.season_label))
        if data.season_label:
            self.season_label.setText(f"• {data.season_label}")

        if not has_groups:
            return

        cols = 3
        for idx, group in enumerate(data.groups):
            row = idx // cols
            col = idx % cols
            section = LeaderSection(group.title, group.stats)
            self.grid.addWidget(section, row, col)

    def _clear_grid(self) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            if widget := item.widget():
                widget.setParent(None)
