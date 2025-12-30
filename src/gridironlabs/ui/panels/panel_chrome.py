"""Panel chrome (minimal).

This is intentionally minimal: a simple box with the app's panel background color
(via QSS) and a single body layout. No title/header/separator/slots yet.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QSizePolicy,
    QVBoxLayout,
)

class PanelChrome(QFrame):
    """Minimal panel container (box + body layout)."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PanelChrome")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Body area
        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)
        root.addLayout(self.body_layout, 1)


