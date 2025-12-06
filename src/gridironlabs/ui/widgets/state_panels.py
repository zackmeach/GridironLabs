"""Reusable UI states: loading, empty, and error."""

from __future__ import annotations

try:
    from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover
    QLabel = QVBoxLayout = QWidget = object  # type: ignore


class LoadingPanel(QWidget):  # type: ignore[misc]
    def __init__(self, message: str = "Loading...") -> None:
        super().__init__()
        if QWidget is object:
            return
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(message))


class EmptyPanel(QWidget):  # type: ignore[misc]
    def __init__(self, message: str = "No data yet") -> None:
        super().__init__()
        if QWidget is object:
            return
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(message))


class ErrorPanel(QWidget):  # type: ignore[misc]
    def __init__(self, message: str = "Something went wrong") -> None:
        super().__init__()
        if QWidget is object:
            return
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(message))
