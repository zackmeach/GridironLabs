"""Callout strip used for status summaries (e.g., 'LOSS', date)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QWidget


class CalloutStrip(QFrame):
    def __init__(
        self,
        *,
        left_text: str,
        right_text: str | None = None,
        intent: str = "neutral",  # neutral|success|warning|danger
    ) -> None:
        super().__init__()
        self.setObjectName("CalloutStrip")
        self.setProperty("intent", str(intent))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(32)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        self.left_label = QLabel(left_text)
        self.left_label.setObjectName("CalloutLeft")
        self.left_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.left_label, 0)

        layout.addStretch(1)

        self.right_label: QLabel | None = None
        if right_text is not None:
            lbl = QLabel(right_text)
            lbl.setObjectName("CalloutRight")
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.right_label = lbl
            layout.addWidget(lbl, 0)


__all__ = ["CalloutStrip"]

