"""Scoreboard widget used in 'Last Game' style panels."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QHBoxLayout, QPushButton, QSizePolicy, QWidget


@dataclass(frozen=True)
class ScoreboardLine:
    team: str
    runs_by_inning: Sequence[int]
    r: int
    h: int
    e: int


class ScoreboardWidget(QFrame):
    def __init__(self, *, innings: int = 9) -> None:
        super().__init__()
        self.setObjectName("ScoreboardWidget")
        self.setProperty("innings", int(innings))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._innings = int(innings)
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(10, 10, 10, 10)
        self._grid.setSpacing(6)

        # Header row
        self._grid.addWidget(self._mk_hdr(""), 0, 0)
        for i in range(1, self._innings + 1):
            self._grid.addWidget(self._mk_hdr(str(i)), 0, i)
        base = self._innings + 1
        self._grid.addWidget(self._mk_hdr("R"), 0, base + 0)
        self._grid.addWidget(self._mk_hdr("H"), 0, base + 1)
        self._grid.addWidget(self._mk_hdr("E"), 0, base + 2)

        self._next_row = 1

    def clear_lines(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            if w := item.widget():
                w.setParent(None)
        # rebuild header
        self.__init__(innings=self._innings)  # type: ignore[misc]

    def set_lines(self, lines: Sequence[ScoreboardLine]) -> None:
        # reset but keep instance
        # Remove everything except header row.
        while self._grid.count():
            item = self._grid.takeAt(0)
            if w := item.widget():
                w.setParent(None)
        # Re-add header row
        self._grid.addWidget(self._mk_hdr(""), 0, 0)
        for i in range(1, self._innings + 1):
            self._grid.addWidget(self._mk_hdr(str(i)), 0, i)
        base = self._innings + 1
        self._grid.addWidget(self._mk_hdr("R"), 0, base + 0)
        self._grid.addWidget(self._mk_hdr("H"), 0, base + 1)
        self._grid.addWidget(self._mk_hdr("E"), 0, base + 2)

        self._next_row = 1
        for line in lines:
            self.add_line(line)

    def add_line(self, line: ScoreboardLine) -> None:
        row = self._next_row
        self._next_row += 1
        self._grid.addWidget(self._mk_cell(line.team, align=Qt.AlignLeft), row, 0)
        innings = list(line.runs_by_inning)[: self._innings]
        innings += [0] * max(0, self._innings - len(innings))
        for i, v in enumerate(innings, start=1):
            self._grid.addWidget(self._mk_cell(str(v), align=Qt.AlignCenter), row, i)
        base = self._innings + 1
        self._grid.addWidget(self._mk_cell(str(line.r), align=Qt.AlignCenter, bold=True), row, base + 0)
        self._grid.addWidget(self._mk_cell(str(line.h), align=Qt.AlignCenter), row, base + 1)
        self._grid.addWidget(self._mk_cell(str(line.e), align=Qt.AlignCenter), row, base + 2)

    @staticmethod
    def _mk_hdr(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("ScoreboardHeaderCell")
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    @staticmethod
    def _mk_cell(text: str, *, align: Qt.Alignment, bold: bool = False) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("ScoreboardCell")
        lbl.setAlignment(align | Qt.AlignVCenter)
        if bold:
            lbl.setProperty("emphasis", "true")
        return lbl


class FooterButtonRow(QWidget):
    """Simple horizontal row of buttons (for replay/highlights/box score patterns)."""

    def __init__(self, labels: Sequence[str]) -> None:
        super().__init__()
        self.setObjectName("FooterButtonRow")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        for text in labels:
            btn = QPushButton(text)
            btn.setObjectName("FooterButton")
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            layout.addWidget(btn)


__all__ = ["FooterButtonRow", "ScoreboardLine", "ScoreboardWidget"]

