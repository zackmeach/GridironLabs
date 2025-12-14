from __future__ import annotations

from typing import Optional, Tuple

from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSlider,
    QSpinBox,
    QVBoxLayout,
)


class TitleLabel(QLabel):
    """Unified title label with configurable style hook."""

    def __init__(
        self,
        text: str,
        *,
        alignment: Qt.Alignment = Qt.AlignLeft | Qt.AlignTop,
        object_name: str = "CardTitlePrimary",
    ) -> None:
        super().__init__(text)
        self.setObjectName(object_name)
        self.setWordWrap(True)
        self.setAlignment(alignment)


class Card(QFrame):
    """Base card shell with optional title and enforced chrome."""

    def __init__(
        self,
        title: Optional[str] = None,
        *,
        role: str = "primary",
        margins: Tuple[int, int, int, int] = (12, 12, 12, 12),
        spacing: int = 10,
        show_separator: bool = True,
        title_alignment: Qt.Alignment = Qt.AlignLeft | Qt.AlignTop,
        title_object_name: str = "CardTitlePrimary",
    ) -> None:
        super().__init__()
        self.setObjectName("Card")
        self.setProperty("card-role", role)

        root = QVBoxLayout(self)
        root.setContentsMargins(*margins)
        root.setSpacing(spacing)

        if title is not None:
            header = QVBoxLayout()
            header.setContentsMargins(0, 0, 0, 0)
            header.setSpacing(6)

            self.title_label = TitleLabel(
                title, alignment=title_alignment, object_name=title_object_name
            )
            header.addWidget(self.title_label)

            if show_separator:
                separator = QFrame()
                separator.setObjectName("CardSeparator")
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Plain)
                separator.setLineWidth(1)
                header.addWidget(separator)

            root.addLayout(header)

        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(spacing)
        root.addLayout(self.body_layout)


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

    def paintEvent(self, event) -> None:  # pragma: no cover - trivial UI
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
    "Card",
    "TitleLabel",
    "AppSwitch",
    "AppCheckbox",
    "AppSlider",
    "AppLineEdit",
    "AppSpinBox",
    "AppComboBox",
]

