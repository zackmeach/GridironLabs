"""Two-column form grid used for settings-like pages."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QSizePolicy, QWidget


class FormGrid(QFrame):
    def __init__(self, *, label_width: int = 260, row_height: int = 34) -> None:
        super().__init__()
        self.setObjectName("FormGrid")
        self._label_width = int(label_width)
        self._row_height = int(row_height)

        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setHorizontalSpacing(12)
        self._grid.setVerticalSpacing(8)

        self._row = 0

    def add_section(self, title: str) -> None:
        lbl = QLabel(title)
        lbl.setObjectName("FormSectionTitle")
        lbl.setProperty("rowRole", "section")
        lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._grid.addWidget(lbl, self._row, 0, 1, 2)
        self._row += 1

    def add_row(self, *, label: str, field: QWidget, caption: str | None = None) -> None:
        key = QLabel(label)
        key.setObjectName("FormLabel")
        key.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        key.setFixedWidth(self._label_width)
        key.setFixedHeight(self._row_height)

        field.setParent(self)
        field.setFixedHeight(self._row_height)

        self._grid.addWidget(key, self._row, 0)
        self._grid.addWidget(field, self._row, 1)
        self._row += 1

        if caption:
            cap = QLabel(caption)
            cap.setObjectName("FormCaption")
            cap.setWordWrap(True)
            cap.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self._grid.addWidget(cap, self._row, 0, 1, 2)
            self._row += 1


__all__ = ["FormGrid"]

