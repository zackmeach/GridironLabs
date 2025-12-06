"""Application bootstrapper for the PySide6 desktop shell."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import TracebackType
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

    def _install_exception_hook(self) -> None:
        """Log unhandled Qt exceptions instead of silently swallowing them."""

        def _handler(
            exc_type: type[BaseException],
            exc_value: BaseException,
            exc_traceback: TracebackType | None,
        ) -> None:
            if self.logger:
                self.logger.exception(
                    "Unhandled exception",
                    exc_info=(exc_type, exc_value, exc_traceback),
                )
            # Fall back to default hook so the process still surfaces errors.
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

        sys.excepthook = _handler

    def _load_stylesheet(self) -> str:
        """Load the packaged QSS theme."""
        resources_dir = Path(__file__).resolve().parent.parent / "resources"
        preferred = resources_dir / f"{self.config.ui_theme}.qss"
        fallback = resources_dir / "theme.qss"
        theme_path = preferred if preferred.exists() else fallback
        try:
            return theme_path.read_text(encoding="utf-8")
        except OSError:
            if self.logger:
                self.logger.warning(
                    "Stylesheet missing; continuing with Qt defaults",
                    extra={"path": str(theme_path)},
                )
            return ""

    @staticmethod
    def _is_offline() -> bool:
        """True when nflreadpy is unavailable; used to display the offline banner."""
        return importlib.util.find_spec("nflreadpy") is None

    def run(self) -> int:
        try:
            from PySide6.QtWidgets import QApplication
        except ImportError as exc:  # pragma: no cover - optional dep at scaffold time
            raise MissingDependencyError("PySide6 is required to launch the UI") from exc

        app = QApplication.instance() or QApplication(sys.argv)
        app.setApplicationName("Gridiron Labs")
        app.setOrganizationName("Gridiron Labs")
        stylesheet = self._load_stylesheet()
        if stylesheet:
            app.setStyleSheet(stylesheet)

        self._install_exception_hook()

        window = GridironLabsMainWindow(
            config=self.config,
            paths=self.paths,
            logger=self.logger,
            offline_mode=self._is_offline(),
        )
        window.showMaximized()
        return app.exec()
