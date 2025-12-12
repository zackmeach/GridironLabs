from __future__ import annotations

from typing import Optional, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


class PanelCard(QFrame):
    """Reusable card with optional title and consistent chrome."""

    def __init__(
        self,
        title: Optional[str] = None,
        *,
        object_name: Optional[str] = None,
        margins: Tuple[int, int, int, int] = (12, 12, 12, 12),
        spacing: int = 10,
        show_separator: bool = True,
        title_alignment: Qt.Alignment = Qt.AlignLeft | Qt.AlignTop,
        title_object_name: str = "PanelCardTitle",
    ) -> None:
        super().__init__()
        self.setObjectName(object_name or "PanelCard")

        root = QVBoxLayout(self)
        root.setContentsMargins(*margins)
        root.setSpacing(spacing)

        if title is not None:
            header = QVBoxLayout()
            header.setContentsMargins(0, 0, 0, 0)
            header.setSpacing(6)

            self.title_label = QLabel(title)
            self.title_label.setObjectName(title_object_name)
            self.title_label.setWordWrap(True)
            self.title_label.setAlignment(title_alignment)
            header.addWidget(self.title_label)

            if show_separator:
                separator = QFrame()
                separator.setObjectName("PanelSeparator")
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Plain)
                separator.setLineWidth(1)
                header.addWidget(separator)

            root.addLayout(header)

        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(spacing)
        root.addLayout(self.body_layout)

