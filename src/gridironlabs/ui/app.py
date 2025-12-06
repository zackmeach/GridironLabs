"""Application bootstrapper for the PySide6 desktop shell."""

from __future__ import annotations

from typing import Any

from gridironlabs.core.config import AppConfig, AppPaths
from gridironlabs.core.errors import MissingDependencyError
from gridironlabs.ui.main_window import GridironLabsMainWindow


class GridironLabsApplication:
    """Thin wrapper to bootstrap the UI with configuration and logging."""

    def __init__(self, *, config: AppConfig, paths: AppPaths, logger: Any) -> None:
        self.config = config
        self.paths = paths
        self.logger = logger

    def run(self) -> int:
        try:
            from PySide6.QtWidgets import QApplication
        except ImportError as exc:  # pragma: no cover - optional dep at scaffold time
            raise MissingDependencyError("PySide6 is required to launch the UI") from exc

        app = QApplication(sys.argv)
        window = GridironLabsMainWindow(config=self.config, paths=self.paths, logger=self.logger)
        window.show()
        return app.exec()
