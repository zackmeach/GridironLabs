"""Segmented tab strip used inside bodies (OOTP-style)."""

from __future__ import annotations

from typing import Callable, Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QHBoxLayout, QPushButton, QSizePolicy


class TabStrip(QFrame):
    tabChanged = Signal(str)  # tab key

    def __init__(self, tabs: Sequence[tuple[str, str]], *, initial: str | None = None) -> None:
        super().__init__()
        self.setObjectName("TabStrip")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(34)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[str, QPushButton] = {}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for key, label in tabs:
            btn = QPushButton(label)
            btn.setObjectName("TabStripButton")
            btn.setCheckable(True)
            btn.setProperty("tabKey", key)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self._group.addButton(btn)
            self._buttons[key] = btn
            layout.addWidget(btn)

        self._group.buttonToggled.connect(self._on_toggled)

        if initial is None and tabs:
            initial = tabs[0][0]
        if initial is not None:
            self.set_active(initial)

    def set_active(self, key: str) -> None:
        if key in self._buttons:
            self._buttons[key].setChecked(True)

    def _on_toggled(self, button: QPushButton, checked: bool) -> None:
        if not checked:
            return
        key = str(button.property("tabKey") or "")
        if key:
            self.tabChanged.emit(key)


__all__ = ["TabStrip"]

