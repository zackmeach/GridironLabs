"""League standings widget with sectioned divisions."""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from gridironlabs.ui.panels.bars.standard_bars import SectionBar
from gridironlabs.ui.assets.logos import get_logo_pixmap
from gridironlabs.ui.widgets.scroll_guard import make_locked_scroll
from gridironlabs.ui.table.columns import ColumnSpec


ROW_H = 26
LOGO_SIZE = 18


STANDINGS_COLUMNS: tuple[ColumnSpec, ...] = (
    ColumnSpec("place", "PLACE", 60, Qt.AlignLeft | Qt.AlignVCenter),
    ColumnSpec("team", "TEAM", 240, Qt.AlignLeft | Qt.AlignVCenter),
    ColumnSpec("w", "W", 50, Qt.AlignRight | Qt.AlignVCenter),
    ColumnSpec("l", "L", 50, Qt.AlignRight | Qt.AlignVCenter),
    ColumnSpec("pct", "%", 70, Qt.AlignRight | Qt.AlignVCenter),
    ColumnSpec("gb", "GB", 60, Qt.AlignRight | Qt.AlignVCenter),
)

# Minimal mapping for the current dummy data. (Can be replaced by real model data later.)
TEAM_ABBR: dict[str, str] = {
    "Buffalo Bills": "BUF",
    "Miami Dolphins": "MIA",
    "New York Jets": "NYJ",
    "New England Patriots": "NE",
    "Baltimore Ravens": "BAL",
    "Cleveland Browns": "CLE",
    "Pittsburgh Steelers": "PIT",
    "Cincinnati Bengals": "CIN",
    "Houston Texans": "HOU",
    "Jacksonville Jaguars": "JAX",
    "Indianapolis Colts": "IND",
    "Tennessee Titans": "TEN",
    "Kansas City Chiefs": "KC",
    "Denver Broncos": "DEN",
    "Las Vegas Raiders": "LV",
    "Los Angeles Chargers": "LAC",
    "Dallas Cowboys": "DAL",
    "Philadelphia Eagles": "PHI",
    "New York Giants": "NYG",
    "Washington Commanders": "WAS",
    "Green Bay Packers": "GB",
    "Minnesota Vikings": "MIN",
    "Detroit Lions": "DET",
    "Chicago Bears": "CHI",
    "New Orleans Saints": "NO",
    "Tampa Bay Buccaneers": "TB",
    "Atlanta Falcons": "ATL",
    "Carolina Panthers": "CAR",
    "San Francisco 49ers": "SF",
    "Seattle Seahawks": "SEA",
    "Los Angeles Rams": "LAR",
    "Arizona Cardinals": "ARI",
}


class StandingsHeaderRow(QFrame):
    """Column header row for standings (aligns with StandingsRow)."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("StandingsHeaderRow")
        self.setFixedHeight(ROW_H)

        layout = QHBoxLayout(self)
        # Important: do NOT add horizontal margins here.
        # The containing bar (TertiaryHeaderBar) already applies the canonical inset via QSS padding.
        # Adding margins here would double-inset the header relative to the rows.
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        def add_cell(text: str, width: int, align: Qt.Alignment) -> None:
            lbl = QLabel(text)
            lbl.setObjectName("StandingsHeaderCell")
            lbl.setFixedWidth(width)
            lbl.setAlignment(align)
            layout.addWidget(lbl)

        for col in STANDINGS_COLUMNS:
            add_cell(col.label, col.width, col.alignment)

        layout.addStretch(1)


class StandingsRow(QFrame):
    """A single row in the standings table."""
    
    def __init__(
        self, 
        place: str, 
        team: str, 
        w: str,
        l: str,
        pct: str, 
        gb: str,
        highlight: bool = False,
        on_click: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("StandingsRow")
        self.setFixedHeight(ROW_H)  # Match header height for consistency
        self._team = team
        self._on_click = on_click

        if self._on_click is not None:
            self.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0) # Remove vertical padding to rely on fixed height
        layout.setSpacing(4)
        
        values: dict[str, str] = {
            "place": place,
            "team": team,
            "w": w,
            "l": l,
            "pct": pct,
            "gb": gb,
        }

        # Helper to create consistently styled cells
        def add_cell(text: str, width: int | None = None, align: Qt.Alignment = Qt.AlignLeft) -> QLabel:
            lbl = QLabel(text)
            lbl.setObjectName("StandingsCell")
            # Make the row itself the click target.
            lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            if width:
                lbl.setFixedWidth(width)
            lbl.setAlignment(align)
            layout.addWidget(lbl)
            return lbl

        for col in STANDINGS_COLUMNS:
            if col.key == "team":
                # TEAM column: logo + team name (kept within the TEAM column width)
                team_cell = QWidget()
                team_cell.setFixedWidth(col.width)
                team_cell.setAttribute(Qt.WA_TransparentForMouseEvents, True)
                team_cell_layout = QHBoxLayout(team_cell)
                team_cell_layout.setContentsMargins(0, 0, 0, 0)
                team_cell_layout.setSpacing(6)

                logo = QLabel()
                logo.setObjectName("StandingsTeamLogo")
                logo.setFixedSize(LOGO_SIZE, LOGO_SIZE)
                logo.setAlignment(Qt.AlignCenter)
                logo.setAttribute(Qt.WA_TransparentForMouseEvents, True)

                abbr = TEAM_ABBR.get(team, "")
                pixmap = get_logo_pixmap(abbr, size=LOGO_SIZE) if abbr else None
                if pixmap is not None:
                    logo.setPixmap(pixmap)

                name = QLabel(team)
                name.setObjectName("StandingsTeamCell")
                name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                name.setAttribute(Qt.WA_TransparentForMouseEvents, True)

                team_cell_layout.addWidget(logo, 0, Qt.AlignVCenter)
                team_cell_layout.addWidget(name, 1, Qt.AlignVCenter)

                layout.addWidget(team_cell)
                continue

            add_cell(values.get(col.key, ""), width=col.width, align=col.alignment)
        
        layout.addStretch(1)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton and self._on_click is not None:
            self._on_click(self._team)
            event.accept()
            return
        super().mousePressEvent(event)


class LeagueStandingsWidget(QFrame):
    """Scrollable container for division standings."""

    def __init__(self, *, on_team_click: Callable[[str], None] | None = None) -> None:
        super().__init__()
        self.setObjectName("LeagueStandingsWidget")
        self._on_team_click = on_team_click
        
        # Container for the vertical stack of sections
        self.content = QWidget()
        self.content.setObjectName("StandingsContent")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # Scroll area for arbitrary number of divisions (locked surface behavior).
        self.scroll = make_locked_scroll(self.content, threshold_px=1, normal_policy=Qt.ScrollBarAsNeeded)
        self.scroll.setParent(self)
        
        # Main layout puts scroll area in frame
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll)

    def add_division(self, name: str, teams: list[tuple[str, str, str, str, str, str]]) -> None:
        """Add a division section with a header and rows of teams.
        
        Teams tuple: (place, team, w, l, pct, gb)
        """
        
        # 1. Section Header
        # Add a small spacer before the section if it's not the first one
        if self.content_layout.count() > 0:
             # Just let the natural layout spacing handle it, or force 0 if we want tight packing
             pass

        header = SectionBar(title=name)
        self.content_layout.addWidget(header)
        
        # 2. Team Rows
        for place, team, w, l, pct, gb in teams:
            row = StandingsRow(place, team, w, l, pct, gb, on_click=self._on_team_click)
            self.content_layout.addWidget(row)
        
        # Add a tiny spacer after the group? 
        # For now, let the next section bar provide the visual break.

