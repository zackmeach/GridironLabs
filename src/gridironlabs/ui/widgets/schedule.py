"""League Schedule panel body (Home page).

UI contract reference: repo root `image.png`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from gridironlabs.core.models import GameSummary
from gridironlabs.core.nfl_structure import team_name_for_abbr
from gridironlabs.ui.assets.logos import get_logo_pixmap
from gridironlabs.ui.panels.bars.standard_bars import SectionBar
from gridironlabs.ui.widgets.scroll_guard import make_locked_scroll


LOGO_SIZE = 22
ROW_H = 56
DAY_ROW_H = 44
COLUMN_GAP = 8
ROW_MARGIN_X = 8
SCORE_GAP = 6

# Column widths tuned for the panel layout (fit within the Home right rail).
DATE_W = 160
HOME_W = 108
AWAY_W = 108
TIME_W = 72
SCORE_W = 96


PLAYOFF_ORDER = {
    "wild card": 1,
    "wildcard": 1,
    "divisional": 2,
    "conference": 3,
    "super bowl": 4,
    "superbowl": 4,
}

PLAYOFF_LABELS = {
    "wild card": "Wildcard Round",
    "wildcard": "Wildcard Round",
    "divisional": "Divisional Round",
    "conference": "Conference Round",
    "super bowl": "Super Bowl",
    "superbowl": "Super Bowl",
}


def _fmt_day(dt: datetime) -> str:
    # Example: "Thu, Dec 4" (no leading zero on day).
    day = dt.strftime("%a")
    month = dt.strftime("%b")
    d = int(dt.day)
    return f"{day}, {month} {d}"


def _fmt_time(dt: datetime) -> str:
    # Example: "7:15 PM" (no leading zero on hour).
    hour = dt.strftime("%I").lstrip("0") or "12"
    return f"{hour}{dt.strftime(':%M %p')}"


def _display_team(abbr: str) -> str:
    name = team_name_for_abbr(abbr) or abbr
    # Reference uses "DAL Cowboys" style.
    parts = str(name).split()
    nickname = parts[-1] if parts else abbr
    return f"{abbr} {nickname}"


@dataclass(frozen=True)
class WeekGroupKey:
    """A stable key representing a navigable schedule group."""

    season: int
    kind: str  # "preseason" | "regular" | "postseason"
    order: int
    label: str


def _week_label(game: GameSummary) -> str:
    if game.is_postseason:
        raw = (game.playoff_round or "").strip()
        if raw:
            key = raw.lower().replace("-", " ").strip()
            return PLAYOFF_LABELS.get(key, raw if raw.endswith("Round") else f"{raw} Round")
        return f"Playoffs (Week {game.week})"
    # Preseason encoding: week <= 0.
    if game.week <= 0:
        wk = abs(int(game.week)) or 1
        return f"Preseason Week {wk}"
    return f"Week {int(game.week)}"


def _group_key_for(game: GameSummary) -> WeekGroupKey:
    if game.is_postseason:
        raw = (game.playoff_round or "").strip()
        key = raw.lower().replace("-", " ").strip()
        order = PLAYOFF_ORDER.get(key, 100 + int(game.week))
        return WeekGroupKey(season=game.season, kind="postseason", order=1000 + order, label=_week_label(game))
    if game.week <= 0:
        wk = abs(int(game.week)) or 1
        return WeekGroupKey(season=game.season, kind="preseason", order=wk, label=f"Preseason Week {wk}")
    return WeekGroupKey(season=game.season, kind="regular", order=100 + int(game.week), label=f"Week {int(game.week)}")


class ScheduleWeekNavigator(QWidget):
    """◀ WeekLabel ▶ control strip for the panel header."""

    def __init__(self, *, on_prev, on_next) -> None:  # noqa: ANN001 - Qt callback shape
        super().__init__()
        self.setObjectName("ScheduleWeekNavigator")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.prev_btn = QToolButton()
        self.prev_btn.setObjectName("ScheduleWeekPrev")
        self.prev_btn.setText("◀")
        self.prev_btn.setAutoRaise(True)
        self.prev_btn.clicked.connect(on_prev)

        self.label = QLabel("Week")
        self.label.setObjectName("ScheduleWeekLabel")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self.next_btn = QToolButton()
        self.next_btn.setObjectName("ScheduleWeekNext")
        self.next_btn.setText("▶")
        self.next_btn.setAutoRaise(True)
        self.next_btn.clicked.connect(on_next)

        layout.addWidget(self.prev_btn)
        layout.addWidget(self.label)
        layout.addWidget(self.next_btn)

    def set_label(self, text: str) -> None:
        self.label.setText(str(text))


class ScheduleRow(QFrame):
    def __init__(self, *, game: GameSummary) -> None:
        super().__init__()
        self.setObjectName("ScheduleRow")
        self.setFixedHeight(ROW_H)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(ROW_MARGIN_X, 0, ROW_MARGIN_X, 0)
        layout.setSpacing(COLUMN_GAP)

        date_spacer = QWidget()
        date_spacer.setObjectName("ScheduleDateSpacer")
        date_spacer.setFixedWidth(DATE_W)
        date_spacer.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        def team_cell(abbr: str, *, width: int) -> QWidget:
            cell = QWidget()
            cell.setObjectName("ScheduleTeamCell")
            cell.setFixedWidth(int(width))
            cell.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            hl = QHBoxLayout(cell)
            hl.setContentsMargins(0, 0, 0, 0)
            hl.setSpacing(COLUMN_GAP)

            logo = QLabel()
            logo.setObjectName("ScheduleTeamLogo")
            logo.setFixedSize(LOGO_SIZE, LOGO_SIZE)
            logo.setAlignment(Qt.AlignCenter)
            logo.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            pm = get_logo_pixmap(abbr, size=LOGO_SIZE)
            if pm is not None:
                logo.setPixmap(pm)

            name = QLabel(_display_team(abbr))
            name.setObjectName("ScheduleTeamLabel")
            name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            name.setMinimumWidth(0)
            name.setAttribute(Qt.WA_TransparentForMouseEvents, True)

            hl.addWidget(logo, 0, Qt.AlignVCenter)
            hl.addWidget(name, 1, Qt.AlignVCenter)
            return cell

        home = team_cell(game.home_team, width=HOME_W)
        away = team_cell(game.away_team, width=AWAY_W)

        time_lbl = QLabel(_fmt_time(game.start_time))
        time_lbl.setObjectName("ScheduleTime")
        time_lbl.setFixedWidth(TIME_W)
        time_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        time_lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        score_cell = QWidget()
        score_cell.setObjectName("ScheduleScoreCell")
        score_cell.setFixedWidth(SCORE_W)
        score_cell.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        sl = QHBoxLayout(score_cell)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(SCORE_GAP)

        # Score rendering: scheduled shows "—"; finals show "H - A" with logos flanking.
        if str(game.status).lower() == "final" and game.home_score is not None and game.away_score is not None:
            hlogo = QLabel()
            hlogo.setObjectName("ScheduleScoreLogo")
            hlogo.setFixedSize(LOGO_SIZE, LOGO_SIZE)
            hlogo.setAlignment(Qt.AlignCenter)
            pm = get_logo_pixmap(game.home_team, size=LOGO_SIZE)
            if pm is not None:
                hlogo.setPixmap(pm)

            alogo = QLabel()
            alogo.setObjectName("ScheduleScoreLogo")
            alogo.setFixedSize(LOGO_SIZE, LOGO_SIZE)
            alogo.setAlignment(Qt.AlignCenter)
            pm2 = get_logo_pixmap(game.away_team, size=LOGO_SIZE)
            if pm2 is not None:
                alogo.setPixmap(pm2)

            score_text = QLabel(f"{int(game.home_score)} - {int(game.away_score)}")
            score_text.setObjectName("ScheduleScore")
            score_text.setAlignment(Qt.AlignCenter)
            score_text.setAttribute(Qt.WA_TransparentForMouseEvents, True)

            sl.addWidget(hlogo, 0, Qt.AlignVCenter)
            sl.addWidget(score_text, 1, Qt.AlignVCenter)
            sl.addWidget(alogo, 0, Qt.AlignVCenter)
            # When final, hide the time column content (still reserve width).
            time_lbl.setText("")
        else:
            score_text = QLabel("—")
            score_text.setObjectName("ScheduleScore")
            score_text.setAlignment(Qt.AlignCenter)
            score_text.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            sl.addWidget(score_text, 1, Qt.AlignVCenter)

        layout.addWidget(date_spacer)
        layout.addWidget(home)
        layout.addWidget(away)
        layout.addWidget(time_lbl)
        layout.addWidget(score_cell)
        layout.addStretch(1)


class ScheduleDayHeaderRow(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ScheduleDayHeaderRow")
        self.setFixedHeight(DAY_ROW_H)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(ROW_MARGIN_X, 0, ROW_MARGIN_X, 0)
        layout.setSpacing(COLUMN_GAP)

        date_spacer = QWidget()
        date_spacer.setObjectName("ScheduleDateSpacer")
        date_spacer.setFixedWidth(DATE_W)
        date_spacer.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        def header_label(text: str, *, width: int) -> QLabel:
            label = QLabel(text)
            label.setObjectName("ScheduleHeaderLabel")
            label.setFixedWidth(int(width))
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            return label

        layout.addWidget(date_spacer)
        layout.addWidget(header_label("Home", width=HOME_W))
        layout.addWidget(header_label("Away", width=AWAY_W))
        layout.addWidget(header_label("Time", width=TIME_W))
        layout.addWidget(header_label("Score", width=SCORE_W))
        layout.addStretch(1)


class LeagueScheduleWidget(QFrame):
    """Scrollable schedule body grouped by day for the selected week group."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("LeagueScheduleWidget")
        self._games: list[GameSummary] = []
        self._groups: list[WeekGroupKey] = []
        self._group_index = 0

        self.content = QWidget()
        self.content.setObjectName("ScheduleContent")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        self.scroll = make_locked_scroll(self.content, threshold_px=1, normal_policy=Qt.ScrollBarAsNeeded)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll)

    def set_games(self, games: Iterable[GameSummary]) -> None:
        self._games = list(games)
        self._rebuild_groups()
        self._group_index = 0
        self._render()

    def has_groups(self) -> bool:
        return bool(self._groups)

    def current_group_label(self) -> str:
        if not self._groups:
            return "Week"
        return self._groups[self._group_index].label

    def prev_group(self) -> None:
        if not self._groups:
            return
        self._group_index = max(0, self._group_index - 1)
        self._render()

    def next_group(self) -> None:
        if not self._groups:
            return
        self._group_index = min(len(self._groups) - 1, self._group_index + 1)
        self._render()

    def _rebuild_groups(self) -> None:
        if not self._games:
            self._groups = []
            return
        latest_season = max(g.season for g in self._games)
        season_games = [g for g in self._games if g.season == latest_season]

        keys = {_group_key_for(g) for g in season_games}
        # Stable ordering: preseason, regular, playoffs (using order field).
        self._groups = sorted(keys, key=lambda k: (k.season, k.order, k.label))

    def games_for_current_group(self) -> list[GameSummary]:
        if not self._groups or not self._games:
            return []
        key = self._groups[self._group_index]
        latest_season = key.season
        season_games = [g for g in self._games if g.season == latest_season]
        return [g for g in season_games if _group_key_for(g) == key]

    def _clear_content(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if w := item.widget():
                w.setParent(None)

    def _render(self) -> None:
        self._clear_content()
        games = sorted(self.games_for_current_group(), key=lambda g: g.start_time)
        if not games:
            empty = QLabel("No games loaded. Generate data with scripts/generate_fake_nfl_data.py.")
            empty.setObjectName("ScheduleEmptyLabel")
            empty.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            empty.setContentsMargins(12, 12, 12, 12)
            self.content_layout.addWidget(empty)
            self.content_layout.addStretch(1)
            return

        # Group by calendar day.
        by_day: dict[str, list[GameSummary]] = {}
        day_order: list[str] = []
        for g in games:
            label = _fmt_day(g.start_time)
            if label not in by_day:
                by_day[label] = []
                day_order.append(label)
            by_day[label].append(g)

        for day_label in day_order:
            bar = SectionBar(day_label)
            bar.setFixedHeight(DAY_ROW_H)
            bar.setProperty("scheduleVariant", "schedule")
            self.content_layout.addWidget(bar)
            self.content_layout.addWidget(ScheduleDayHeaderRow())
            for g in by_day[day_label]:
                self.content_layout.addWidget(ScheduleRow(game=g))

        self.content_layout.addStretch(1)


__all__ = ["LeagueScheduleWidget", "ScheduleWeekNavigator"]
