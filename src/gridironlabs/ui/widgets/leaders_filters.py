"""OOTP-style dropdown filter strip for the League Leaders panel."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QWidget

from gridironlabs.core.nfl_structure import list_conferences, list_divisions, list_teams
from gridironlabs.ui.widgets.base_components import AppComboBox


@dataclass(frozen=True)
class LeadersFilters:
    age_key: str  # reserved for future (requires player age/rookie metadata)
    conference: str | None  # "AFC" | "NFC" | None
    division: str | None  # e.g. "AFC North" | None
    team_abbr: str | None  # e.g. "TB" | None


class LeadersFilterBar(QWidget):
    """Compact filter row: Age / Conference / Division / Team."""

    def __init__(self, *, on_change: Callable[[LeadersFilters], None]) -> None:
        super().__init__()
        self.setObjectName("LeadersFilterBar")
        self._on_change = on_change
        self._updating = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.age_combo = AppComboBox()
        self.age_combo.setFixedWidth(170)
        self.age_combo.addItem("All ages", "all")
        self.age_combo.addItem("Rookies", "rookies")
        self.age_combo.addItem("25 and under", "u25")
        self.age_combo.addItem("Over 25", "o25")
        self.age_combo.addItem("Over 30", "o30")
        self.age_combo.addItem("Over 35", "o35")
        self.age_combo.setEnabled(False)
        self.age_combo.setToolTip("Age (coming soon): requires player age/rookie metadata.")

        self.conf_combo = AppComboBox()
        self.conf_combo.setFixedWidth(165)
        self.conf_combo.addItem("All conferences", None)
        for conf in list_conferences():
            self.conf_combo.addItem(conf, conf)
        self.conf_combo.setToolTip("Conference filter (AFC/NFC).")

        self.div_combo = AppComboBox()
        self.div_combo.setFixedWidth(185)
        self.div_combo.setToolTip("Division filter (e.g., AFC North).")

        self.team_combo = AppComboBox()
        self.team_combo.setFixedWidth(220)
        self.team_combo.setToolTip("Team filter (alphabetical).")

        layout.addWidget(self.age_combo)
        layout.addWidget(self.conf_combo)
        layout.addWidget(self.div_combo)
        layout.addWidget(self.team_combo)
        layout.addStretch(1)

        self.conf_combo.currentIndexChanged.connect(self._on_conference_changed)
        self.div_combo.currentIndexChanged.connect(self._on_division_changed)
        self.team_combo.currentIndexChanged.connect(self._emit)
        # Age is disabled for now, but wire it for future enablement.
        self.age_combo.currentIndexChanged.connect(self._emit)

        # Initial population for dependent combos.
        self._rebuild_dependent_options(preserve_selection=False)
        self._emit()

    def current_filters(self) -> LeadersFilters:
        age_key = self.age_combo.currentData() or "all"
        conference = self.conf_combo.currentData()
        division = self.div_combo.currentData()
        team_abbr = self.team_combo.currentData()
        return LeadersFilters(
            age_key=str(age_key),
            conference=str(conference) if conference else None,
            division=str(division) if division else None,
            team_abbr=str(team_abbr) if team_abbr else None,
        )

    def _on_conference_changed(self) -> None:
        self._rebuild_dependent_options(preserve_selection=True)
        self._emit()

    def _on_division_changed(self) -> None:
        self._rebuild_team_options(preserve_selection=True)
        self._emit()

    def _rebuild_dependent_options(self, *, preserve_selection: bool) -> None:
        # Conference affects division + team option sets.
        prev_div = self.div_combo.currentData() if preserve_selection else None
        prev_team = self.team_combo.currentData() if preserve_selection else None

        self._updating = True
        try:
            self._rebuild_division_options(prev_division=prev_div)
            self._rebuild_team_options(prev_team_abbr=prev_team, preserve_selection=preserve_selection)
        finally:
            self._updating = False

    def _rebuild_division_options(self, *, prev_division: str | None) -> None:
        conference = self.conf_combo.currentData()
        allowed = list_divisions(conference=conference)

        self.div_combo.blockSignals(True)
        try:
            self.div_combo.clear()
            self.div_combo.addItem("All divisions", None)
            for div in allowed:
                self.div_combo.addItem(div, div)

            if prev_division and prev_division in allowed:
                self._set_combo_by_data(self.div_combo, prev_division)
            else:
                self._set_combo_by_data(self.div_combo, None)
        finally:
            self.div_combo.blockSignals(False)

    def _rebuild_team_options(
        self,
        *,
        prev_team_abbr: str | None = None,
        preserve_selection: bool,
    ) -> None:
        conference = self.conf_combo.currentData()
        division = self.div_combo.currentData()

        teams = list_teams(conference=conference, division=division)
        allowed = [t.abbr for t in teams]

        self.team_combo.blockSignals(True)
        try:
            self.team_combo.clear()
            self.team_combo.addItem("All teams", None)
            for t in teams:
                self.team_combo.addItem(t.name, t.abbr)

            if preserve_selection and prev_team_abbr and prev_team_abbr in allowed:
                self._set_combo_by_data(self.team_combo, prev_team_abbr)
            else:
                self._set_combo_by_data(self.team_combo, None)
        finally:
            self.team_combo.blockSignals(False)

    @staticmethod
    def _set_combo_by_data(combo: AppComboBox, data: object) -> None:
        for i in range(combo.count()):
            if combo.itemData(i) == data:
                combo.setCurrentIndex(i)
                return
        combo.setCurrentIndex(0)

    def _emit(self) -> None:
        if self._updating:
            return
        self._on_change(self.current_filters())


__all__ = ["LeadersFilters", "LeadersFilterBar"]

