from __future__ import annotations

from PySide6 import QtCore, QtWidgets


class StatePlaceholder(QtWidgets.QFrame):
    """
    Simple reusable loading/empty/error panel.
    """

    def __init__(
        self,
        title: str,
        body: str,
        state: str = "info",
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("statePlaceholder")
        self.setProperty("state", state)
        self._build_ui(title, body)

    def _build_ui(self, title: str, body: str) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(24, 24, 24, 24)

        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setObjectName("stateTitle")
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.body_label = QtWidgets.QLabel(body)
        self.body_label.setObjectName("stateBody")
        self.body_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.body_label.setWordWrap(True)

        layout.addWidget(self.title_label)
        layout.addWidget(self.body_label)


class InfoBanner(QtWidgets.QFrame):
    """
    Inline banner for environment/runtime hints (e.g., offline mode).
    """

    def __init__(self, text: str, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("infoBanner")
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        label = QtWidgets.QLabel(text)
        label.setObjectName("infoBannerLabel")
        layout.addWidget(label)
        layout.addStretch()
