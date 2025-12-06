"""Main window scaffold for the desktop UI."""

from __future__ import annotations

from typing import Any

from gridironlabs.core.config import AppConfig, AppPaths
from gridironlabs.ui.widgets.navigation import NavigationBar
from gridironlabs.ui.widgets.state_panels import EmptyPanel

try:
    from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover - PySide6 optional at scaffold time
    QMainWindow = QVBoxLayout = QWidget = object  # type: ignore


class GridironLabsMainWindow(QMainWindow):  # type: ignore[misc]
    """Wireframe window for future widgets."""

    def __init__(self, *, config: AppConfig, paths: AppPaths, logger: Any) -> None:
        super().__init__()
        self.config = config
        self.paths = paths
        self.logger = logger

        if QMainWindow is object:  # PySide6 missing
            return

        self.setWindowTitle("Gridiron Labs")
        self.resize(1280, 800)

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.addWidget(NavigationBar(on_home=self._on_home))
        layout.addWidget(self._placeholder_content())
        self.setCentralWidget(container)

    def _placeholder_content(self) -> QWidget:
        if QWidget is object:
            return object()  # type: ignore[return-value]
        return EmptyPanel("Content area placeholder. Wire views here.")

    def _on_home(self) -> None:
        if self.logger:
            self.logger.info("Home clicked (placeholder)")
