"""Persistent navigation bar placeholder."""

from __future__ import annotations

from typing import Callable

try:
    from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QHBoxLayout, QWidget
except ImportError:  # pragma: no cover - PySide6 optional at scaffold time
    QLabel = QLineEdit = QPushButton = QHBoxLayout = QWidget = object  # type: ignore


class NavigationBar(QWidget):  # type: ignore[misc]
    """Minimal stub; will be replaced with full nav experience."""

    def __init__(
        self,
        on_home: Callable[[], None] | None = None,
        on_back: Callable[[], None] | None = None,
        on_forward: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        if QWidget is object:  # PySide6 missing
            return
        layout = QHBoxLayout(self)
        layout.addWidget(QPushButton("Home", clicked=on_home))
        layout.addWidget(QPushButton("◀", clicked=on_back))
        layout.addWidget(QPushButton("▶", clicked=on_forward))
        layout.addWidget(QLabel("Search"))
        layout.addWidget(QLineEdit(placeholderText="Players, teams, coaches"))
        layout.addStretch(1)
