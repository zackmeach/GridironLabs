"""League leaders widget (Home page) with per-category sortable stat columns."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from gridironlabs.core.models import EntitySummary
from gridironlabs.ui.panels.bars.standard_bars import SectionBar
from gridironlabs.ui.widgets.scroll_guard import make_locked_scroll


ROW_H = 26
RANK_W = 56
PLAYER_W = 210
STAT_COL_W: tuple[int, int, int, int, int, int, int] = (86, 74, 74, 74, 68, 64, 72)


def _ordinal(n: int) -> str:
    n = int(n)
    if 10 <= (n % 100) <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _get(stats: Mapping[str, float] | None, key: str) -> float | None:
    if not stats:
        return None
    raw = stats.get(key)
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _pct(numer: float | None, denom: float | None) -> float | None:
    if numer is None or denom is None or denom == 0:
        return None
    return (numer / denom) * 100.0


def _rate(numer: float | None, denom: float | None) -> float | None:
    if numer is None or denom is None or denom == 0:
        return None
    return numer / denom


def _fmt_int(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{int(round(value)):,}"


def _fmt_float(value: float | None, *, places: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:.{places}f}"


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:.0f}%"


@dataclass(frozen=True)
class LeadersStatSpec:
    key: str
    label: str
    direction: str  # "desc" or "asc" (best-to-worst semantics)
    extractor: Callable[[EntitySummary], float | None]
    formatter: Callable[[float | None], str]
    width: int


@dataclass(frozen=True)
class LeadersCategorySpec:
    key: str
    title: str
    row_limit: int
    stats: tuple[LeadersStatSpec, ...]
    predicate: Callable[[EntitySummary], bool]


class _ClickableLabel(QLabel):
    def __init__(self, text: str, *, on_click: Callable[[], None]) -> None:
        super().__init__(text)
        self._on_click = on_click
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            self._on_click()
            event.accept()
            return
        super().mousePressEvent(event)


class LeadersBarStatHeaderStrip(QWidget):
    """Clickable stat headers rendered inside the category `SectionBar`."""

    def __init__(
        self,
        *,
        stats: tuple[LeadersStatSpec, ...],
        on_stat_selected: Callable[[str], None],
        active_stat_key: str,
    ) -> None:
        super().__init__()
        self.setObjectName("LeadersBarStatHeaderStrip")
        self._cells_by_key: dict[str, QLabel] = {}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        for spec in stats:
            def _make_handler(stat_key: str) -> Callable[[], None]:
                return lambda: on_stat_selected(stat_key)

            cell = _ClickableLabel(spec.label, on_click=_make_handler(spec.key))
            cell.setObjectName("LeadersBarStatHeader")
            cell.setFixedWidth(spec.width)
            cell.setAlignment(Qt.AlignCenter)
            cell.setProperty("selected", spec.key == active_stat_key)
            layout.addWidget(cell)
            self._cells_by_key[spec.key] = cell

        layout.addStretch(1)

    def set_active(self, active_stat_key: str) -> None:
        for key, cell in self._cells_by_key.items():
            cell.setProperty("selected", key == active_stat_key)
            cell.style().unpolish(cell)
            cell.style().polish(cell)
            cell.update()


class LeadersRow(QFrame):
    def __init__(
        self,
        *,
        rank: int,
        player: EntitySummary,
        stats: tuple[LeadersStatSpec, ...],
        on_player_click: Callable[[str], None] | None,
    ) -> None:
        super().__init__()
        self.setObjectName("LeadersRow")
        self.setFixedHeight(ROW_H)
        self._player_name = player.name
        self._on_player_click = on_player_click

        if self._on_player_click is not None:
            self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(4)

        rank_lbl = QLabel(_ordinal(rank))
        rank_lbl.setObjectName("LeadersCellRank")
        rank_lbl.setFixedWidth(RANK_W)
        rank_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        rank_lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        layout.addWidget(rank_lbl)

        name_lbl = QLabel(player.name)
        name_lbl.setObjectName("LeadersCellPlayer")
        name_lbl.setFixedWidth(PLAYER_W)
        name_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        name_lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        layout.addWidget(name_lbl)

        for spec in stats:
            val = spec.extractor(player)
            cell = QLabel(spec.formatter(val))
            cell.setObjectName("LeadersCell")
            cell.setFixedWidth(spec.width)
            # Numeric columns: right aligned for cleaner columnar reading.
            cell.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            cell.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            layout.addWidget(cell)

        layout.addStretch(1)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton and self._on_player_click is not None:
            self._on_player_click(self._player_name)
            event.accept()
            return
        super().mousePressEvent(event)


class CategorySection(QFrame):
    def __init__(
        self,
        *,
        spec: LeadersCategorySpec,
        players: list[EntitySummary],
        on_player_click: Callable[[str], None] | None,
    ) -> None:
        super().__init__()
        self.setObjectName("LeadersCategorySection")
        self.setProperty("categoryKey", spec.key)
        self._spec = spec
        self._players = players
        self._on_player_click = on_player_click

        self._active_stat_key = spec.stats[0].key

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._bar = SectionBar(title=spec.title)
        self._bar.setProperty("leadersVariant", "leaders")
        self._bar.left_slot.setSpacing(4)
        # Make the title occupy the "RANK + PLAYER" visual space so stat headers align.
        self._bar.title_label.setFixedWidth(RANK_W + PLAYER_W + 4)
        self._layout.addWidget(self._bar)

        self._stat_strip = LeadersBarStatHeaderStrip(
            stats=spec.stats,
            on_stat_selected=self._on_stat_selected,
            active_stat_key=self._active_stat_key,
        )
        # Render stat headers inside the yellow bar row.
        self._bar.add_left(self._stat_strip)

        self._rows_container = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_container)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(0)
        self._layout.addWidget(self._rows_container)

        self._rebuild_rows()

    def set_players(self, players: list[EntitySummary]) -> None:
        self._players = players
        self._rebuild_rows()

    def _on_stat_selected(self, stat_key: str) -> None:
        # No toggling: clicking again keeps the same best-to-worst ranking.
        if stat_key == self._active_stat_key:
            return
        self._active_stat_key = stat_key
        self._stat_strip.set_active(stat_key)
        self._rebuild_rows()

    def _rebuild_rows(self) -> None:
        while self._rows_layout.count():
            item = self._rows_layout.takeAt(0)
            if w := item.widget():
                w.setParent(None)

        candidates = [p for p in self._players if self._spec.predicate(p)]
        stat = next((s for s in self._spec.stats if s.key == self._active_stat_key), self._spec.stats[0])

        def sort_key(p: EntitySummary):
            v = stat.extractor(p)
            missing = v is None
            if stat.direction == "asc":
                return (missing, v if v is not None else 0.0)
            return (missing, -(v if v is not None else 0.0))

        ranked = sorted(candidates, key=sort_key)[: self._spec.row_limit]

        if len(ranked) < self._spec.row_limit:
            for i in range(self._spec.row_limit - len(ranked)):
                ranked.append(
                    EntitySummary(
                        id=f"placeholder-{self._spec.key}-{i}",
                        name="—",
                        entity_type="player",
                    )
                )

        for idx, player in enumerate(ranked, start=1):
            self._rows_layout.addWidget(
                LeadersRow(rank=idx, player=player, stats=self._spec.stats, on_player_click=self._on_player_click)
            )


def build_default_category_specs() -> tuple[LeadersCategorySpec, ...]:
    def has_any(*keys: str) -> Callable[[EntitySummary], bool]:
        def _pred(p: EntitySummary) -> bool:
            stats = p.stats
            if not stats:
                return False
            return any(k in stats for k in keys)

        return _pred

    def position_in(*positions: str) -> Callable[[EntitySummary], bool]:
        wanted = {p.upper() for p in positions}

        def _pred(p: EntitySummary) -> bool:
            pos = (p.position or "").upper()
            if pos in wanted:
                return True
            return False

        return _pred

    def _wpa(p: EntitySummary) -> float | None:
        return _get(p.stats, "wpa_total")

    passing = (
        LeadersStatSpec(
            key="passing_yards",
            label="PassYds",
            direction="desc",
            extractor=lambda p: _get(p.stats, "passing_yards"),
            formatter=_fmt_int,
            width=STAT_COL_W[0],
        ),
        LeadersStatSpec(
            key="passing_completions",
            label="Comp",
            direction="desc",
            extractor=lambda p: _get(p.stats, "passing_completions"),
            formatter=_fmt_int,
            width=STAT_COL_W[1],
        ),
        LeadersStatSpec(
            key="passing_completion_pct",
            label="Comp%",
            direction="desc",
            extractor=lambda p: _pct(_get(p.stats, "passing_completions"), _get(p.stats, "passing_attempts")),
            formatter=_fmt_pct,
            width=STAT_COL_W[2],
        ),
        LeadersStatSpec(
            key="passing_tds",
            label="PassTD",
            direction="desc",
            extractor=lambda p: _get(p.stats, "passing_tds"),
            formatter=_fmt_int,
            width=STAT_COL_W[3],
        ),
        LeadersStatSpec(
            key="interceptions",
            label="INT",
            direction="asc",
            extractor=lambda p: _get(p.stats, "interceptions"),
            formatter=_fmt_int,
            width=STAT_COL_W[4],
        ),
        LeadersStatSpec(
            key="qbr",
            label="QBR",
            direction="desc",
            extractor=lambda p: _get(p.stats, "qbr"),
            formatter=lambda v: _fmt_float(v, places=1),
            width=STAT_COL_W[5],
        ),
        LeadersStatSpec(
            key="wpa_total",
            label="WPA",
            direction="desc",
            extractor=_wpa,
            formatter=lambda v: _fmt_float(v, places=2),
            width=STAT_COL_W[6],
        ),
    )

    rushing = (
        LeadersStatSpec(
            key="rushing_yards",
            label="RushYds",
            direction="desc",
            extractor=lambda p: _get(p.stats, "rushing_yards"),
            formatter=_fmt_int,
            width=STAT_COL_W[0],
        ),
        LeadersStatSpec(
            key="rushing_attempts",
            label="Att",
            direction="desc",
            extractor=lambda p: _get(p.stats, "rushing_attempts"),
            formatter=_fmt_int,
            width=STAT_COL_W[1],
        ),
        LeadersStatSpec(
            key="rushing_ypa",
            label="Y/Att",
            direction="desc",
            extractor=lambda p: _rate(_get(p.stats, "rushing_yards"), _get(p.stats, "rushing_attempts")),
            formatter=lambda v: _fmt_float(v, places=1),
            width=STAT_COL_W[2],
        ),
        LeadersStatSpec(
            key="rushing_tds",
            label="RushTD",
            direction="desc",
            extractor=lambda p: _get(p.stats, "rushing_tds"),
            formatter=_fmt_int,
            width=STAT_COL_W[3],
        ),
        LeadersStatSpec(
            key="fumbles",
            label="Fum",
            direction="asc",
            extractor=lambda p: _get(p.stats, "fumbles"),
            formatter=_fmt_int,
            width=STAT_COL_W[4],
        ),
        LeadersStatSpec(
            key="rush_20_plus",
            label="20+",
            direction="desc",
            extractor=lambda p: _get(p.stats, "rush_20_plus"),
            formatter=_fmt_int,
            width=STAT_COL_W[5],
        ),
        LeadersStatSpec(
            key="wpa_total",
            label="WPA",
            direction="desc",
            extractor=_wpa,
            formatter=lambda v: _fmt_float(v, places=2),
            width=STAT_COL_W[6],
        ),
    )

    receiving = (
        LeadersStatSpec(
            key="receiving_yards",
            label="RecYds",
            direction="desc",
            extractor=lambda p: _get(p.stats, "receiving_yards"),
            formatter=_fmt_int,
            width=STAT_COL_W[0],
        ),
        LeadersStatSpec(
            key="receptions",
            label="Catches",
            direction="desc",
            extractor=lambda p: _get(p.stats, "receptions"),
            formatter=_fmt_int,
            width=STAT_COL_W[1],
        ),
        LeadersStatSpec(
            key="receiving_targets",
            label="Targets",
            direction="desc",
            extractor=lambda p: _get(p.stats, "receiving_targets"),
            formatter=_fmt_int,
            width=STAT_COL_W[2],
        ),
        LeadersStatSpec(
            key="receiving_catch_pct",
            label="Catch%",
            direction="desc",
            extractor=lambda p: _pct(_get(p.stats, "receptions"), _get(p.stats, "receiving_targets")),
            formatter=_fmt_pct,
            width=STAT_COL_W[3],
        ),
        LeadersStatSpec(
            key="receiving_tds",
            label="RecTD",
            direction="desc",
            extractor=lambda p: _get(p.stats, "receiving_tds"),
            formatter=_fmt_int,
            width=STAT_COL_W[4],
        ),
        LeadersStatSpec(
            key="receiving_yac",
            label="YAC",
            direction="desc",
            extractor=lambda p: _get(p.stats, "receiving_yac"),
            formatter=_fmt_int,
            width=STAT_COL_W[5],
        ),
        LeadersStatSpec(
            key="wpa_total",
            label="WPA",
            direction="desc",
            extractor=_wpa,
            formatter=lambda v: _fmt_float(v, places=2),
            width=STAT_COL_W[6],
        ),
    )

    kicking = (
        LeadersStatSpec(
            key="field_goals_made",
            label="FGM",
            direction="desc",
            extractor=lambda p: _get(p.stats, "field_goals_made"),
            formatter=_fmt_int,
            width=STAT_COL_W[0],
        ),
        LeadersStatSpec(
            key="field_goals_attempted",
            label="FGA",
            direction="desc",
            extractor=lambda p: _get(p.stats, "field_goals_attempted"),
            formatter=_fmt_int,
            width=STAT_COL_W[1],
        ),
        LeadersStatSpec(
            key="fg_made_under_29",
            label="<29",
            direction="desc",
            extractor=lambda p: _get(p.stats, "fg_made_under_29"),
            formatter=_fmt_int,
            width=STAT_COL_W[2],
        ),
        LeadersStatSpec(
            key="fg_made_30_39",
            label="30-39",
            direction="desc",
            extractor=lambda p: _get(p.stats, "fg_made_30_39"),
            formatter=_fmt_int,
            width=STAT_COL_W[3],
        ),
        LeadersStatSpec(
            key="fg_made_40_49",
            label="40-49",
            direction="desc",
            extractor=lambda p: _get(p.stats, "fg_made_40_49"),
            formatter=_fmt_int,
            width=STAT_COL_W[4],
        ),
        LeadersStatSpec(
            key="fg_made_50_plus",
            label="50+",
            direction="desc",
            extractor=lambda p: _get(p.stats, "fg_made_50_plus"),
            formatter=_fmt_int,
            width=STAT_COL_W[5],
        ),
        LeadersStatSpec(
            key="wpa_total",
            label="WPA",
            direction="desc",
            extractor=_wpa,
            formatter=lambda v: _fmt_float(v, places=2),
            width=STAT_COL_W[6],
        ),
    )

    defense = (
        LeadersStatSpec(
            key="tackles",
            label="Tkl",
            direction="desc",
            extractor=lambda p: _get(p.stats, "tackles"),
            formatter=_fmt_int,
            width=STAT_COL_W[0],
        ),
        LeadersStatSpec(
            key="tackles_for_loss",
            label="TFL",
            direction="desc",
            extractor=lambda p: _get(p.stats, "tackles_for_loss"),
            formatter=_fmt_int,
            width=STAT_COL_W[1],
        ),
        LeadersStatSpec(
            key="sacks",
            label="Sacks",
            direction="desc",
            extractor=lambda p: _get(p.stats, "sacks"),
            formatter=_fmt_int,
            width=STAT_COL_W[2],
        ),
        LeadersStatSpec(
            key="forced_fumbles",
            label="FF",
            direction="desc",
            extractor=lambda p: _get(p.stats, "forced_fumbles"),
            formatter=_fmt_int,
            width=STAT_COL_W[3],
        ),
        LeadersStatSpec(
            key="def_interceptions",
            label="INT",
            direction="desc",
            extractor=lambda p: _get(p.stats, "def_interceptions") or _get(p.stats, "interceptions"),
            formatter=_fmt_int,
            width=STAT_COL_W[4],
        ),
        LeadersStatSpec(
            key="passes_defended",
            label="PD",
            direction="desc",
            extractor=lambda p: _get(p.stats, "passes_defended"),
            formatter=_fmt_int,
            width=STAT_COL_W[5],
        ),
        LeadersStatSpec(
            key="wpa_total",
            label="WPA",
            direction="desc",
            extractor=_wpa,
            formatter=lambda v: _fmt_float(v, places=2),
            width=STAT_COL_W[6],
        ),
    )

    return (
        LeadersCategorySpec(
            key="passing",
            title="PASSING",
            row_limit=5,
            stats=passing,
            predicate=lambda p: position_in("QB")(p) or has_any("passing_yards", "passing_tds")(p),
        ),
        LeadersCategorySpec(
            key="rushing",
            title="RUSHING",
            row_limit=5,
            stats=rushing,
            predicate=lambda p: position_in("RB")(p) or has_any("rushing_yards", "rushing_tds")(p),
        ),
        LeadersCategorySpec(
            key="receiving",
            title="RECEIVING",
            row_limit=5,
            stats=receiving,
            predicate=lambda p: position_in("WR", "TE")(p) or has_any("receiving_yards", "receptions")(p),
        ),
        LeadersCategorySpec(
            key="kicking",
            title="KICKING",
            row_limit=5,
            stats=kicking,
            predicate=lambda p: position_in("K")(p) or has_any("field_goals_attempted", "field_goals_made")(p),
        ),
        LeadersCategorySpec(
            key="defense",
            title="DEFENSE",
            row_limit=12,
            stats=defense,
            predicate=lambda p: position_in("DL", "LB", "CB", "S")(p) or has_any("tackles", "sacks")(p),
        ),
    )


class LeagueLeadersWidget(QFrame):
    def __init__(
        self,
        *,
        on_player_click: Callable[[str], None] | None = None,
        category_specs: tuple[LeadersCategorySpec, ...] | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("LeagueLeadersWidget")
        self._on_player_click = on_player_click

        self._players: list[EntitySummary] = []
        self._category_specs = category_specs or build_default_category_specs()
        self._sections: dict[str, CategorySection] = {}

        self.content = QWidget()
        self.content.setObjectName("LeadersContent")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.scroll = make_locked_scroll(self.content, threshold_px=1, normal_policy=Qt.ScrollBarAsNeeded)
        self.scroll.setParent(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll)

        self._build_sections()

    def set_players(self, players: Iterable[EntitySummary]) -> None:
        self._players = list(players)
        for section in self._sections.values():
            section.set_players(self._players)

    def _build_sections(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if w := item.widget():
                w.setParent(None)
        self._sections.clear()

        for spec in self._category_specs:
            section = CategorySection(spec=spec, players=self._players, on_player_click=self._on_player_click)
            self.content_layout.addWidget(section)
            self._sections[spec.key] = section

        self.content_layout.addStretch(1)


__all__ = [
    "LeagueLeadersWidget",
    "LeadersBarStatHeaderStrip",
    "LeadersCategorySpec",
    "LeadersStatSpec",
    "build_default_category_specs",
]


