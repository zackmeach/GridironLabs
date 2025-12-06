"""Reusable UI states: loading, empty, error, and status banners."""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


class _BaseStatePanel(QFrame):
    """Shared styling wrapper for placeholder states."""

    def __init__(self, title: str, message: str) -> None:
        super().__init__()
        self.setObjectName("StatePanel")
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("StateTitle")
        message_label = QLabel(message)
        message_label.setObjectName("StateSubtitle")
        message_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(message_label)


class LoadingPanel(_BaseStatePanel):
    def __init__(self, message: str = "Loading...") -> None:
        super().__init__("Loading", message)
        self.setObjectName("LoadingPanel")


class EmptyPanel(_BaseStatePanel):
    def __init__(self, message: str = "No data yet") -> None:
        super().__init__("Empty", message)
        self.setObjectName("EmptyPanel")


class ErrorPanel(_BaseStatePanel):
    def __init__(self, message: str = "Something went wrong") -> None:
        super().__init__("Error", message)
        self.setObjectName("ErrorPanel")


class StatusBanner(QFrame):
    """Horizontal banner for offline/placeholder messaging."""

    def __init__(self, message: str, *, severity: str = "info") -> None:
        super().__init__()
        self.setObjectName("StatusBanner")
        self.setProperty("severity", severity)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        label = QLabel(message)
        label.setObjectName("StatusText")
        label.setWordWrap(True)
        layout.addWidget(label)
