"""Application bootstrapper for the PySide6 desktop shell."""

from __future__ import annotations

import sys
from types import TracebackType
from typing import Any

from gridironlabs.core.config import AppConfig, AppPaths
from gridironlabs.core.errors import MissingDependencyError
from gridironlabs import resources as package_resources
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
        theme_name = str(self.config.ui_theme).strip() or "theme"
        if not theme_name.endswith(".qss"):
            theme_name = f"{theme_name}.qss"

        candidates = (theme_name, "theme.qss")
        for candidate in candidates:
            try:
                return package_resources.read_text(candidate, encoding="utf-8")
            except FileNotFoundError:
                continue
            except OSError:
                continue

        if self.logger:
            self.logger.warning(
                "Stylesheet missing; continuing with Qt defaults",
                extra={"candidates": list(candidates)},
            )
        return ""

    def run(self) -> int:
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QFont
        except ImportError as exc:  # pragma: no cover - optional dep at scaffold time
            raise MissingDependencyError("PySide6 is required to launch the UI") from exc

        app = QApplication.instance() or QApplication(sys.argv)
        app.setApplicationName("Gridiron Labs")
        app.setOrganizationName("Gridiron Labs")
        app.setFont(QFont("Roboto Condensed"))
        stylesheet = self._load_stylesheet()
        if stylesheet:
            app.setStyleSheet(stylesheet)

        self._install_exception_hook()

        window = GridironLabsMainWindow(
            config=self.config,
            paths=self.paths,
            logger=self.logger,
        )
        window.showMaximized()
        return app.exec()
