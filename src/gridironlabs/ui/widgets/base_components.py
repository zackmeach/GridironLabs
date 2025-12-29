"""Small reusable UI primitives.

These widgets enforce object names / properties so they pick up styling from the
QSS theme (e.g. `AppLineEdit`, `AppSwitch`).

Legacy panel chrome (`PanelCard`, `Card`) lives in `gridironlabs.ui.widgets.panel_card`.
The forward-looking OOTP-style panel entrypoint is `gridironlabs.ui.panels.PanelChrome`.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLineEdit,
    QSlider,
    QSpinBox,
)


class AppSwitch(QCheckBox):
    """Custom painted switch for consistent on/off controls."""

    def __init__(self, checked: bool = False) -> None:
        super().__init__()
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("AppSwitch")
        self.setFixedHeight(26)

    def sizeHint(self) -> QSize:  # pragma: no cover - trivial UI
        return QSize(46, 28)

    def paintEvent(self, event: Any) -> None:  # pragma: no cover - trivial UI
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        track_rect = QRect(0, (self.height() - 22) // 2, 46, 22)
        track_color = QColor("#7c3aed") if self.isChecked() else QColor("#1f2933")
        if not self.isEnabled():
            track_color = QColor("#111827")
        painter.setPen(Qt.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(track_rect, 11, 11)

        thumb_color = QColor("#f9fafc") if self.isEnabled() else QColor("#6b7280")
        thumb_diameter = 16
        thumb_x = track_rect.left() + 4 if not self.isChecked() else track_rect.right() - thumb_diameter - 3
        thumb_rect = QRect(thumb_x, track_rect.top() + 3, thumb_diameter, thumb_diameter)
        painter.setBrush(thumb_color)
        painter.drawEllipse(thumb_rect)
        painter.end()


class AppCheckbox(QCheckBox):
    """Base checkbox with enforced object name for styling."""

    def __init__(self, text: str = "") -> None:
        super().__init__(text)
        self.setObjectName("AppCheckbox")


class AppSlider(QSlider):
    """Base slider with enforced object name for styling."""

    def __init__(self, orientation: Qt.Orientation = Qt.Horizontal) -> None:
        super().__init__(orientation)
        self.setObjectName("AppSlider")


class AppLineEdit(QLineEdit):
    """Base line edit with enforced object name for styling."""

    def __init__(self, text: str = "") -> None:
        super().__init__(text)
        self.setObjectName("AppLineEdit")


class AppSpinBox(QSpinBox):
    """Base spin box with enforced object name for styling."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("AppSpinBox")


class AppComboBox(QComboBox):
    """Base combo box with enforced object name for styling."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("AppComboBox")


__all__ = [
    "AppSwitch",
    "AppCheckbox",
    "AppSlider",
    "AppLineEdit",
    "AppSpinBox",
    "AppComboBox",
]

