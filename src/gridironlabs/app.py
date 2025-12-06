from __future__ import annotations

import importlib.util
import logging
import sys
from dataclasses import dataclass
from typing import Iterable

from PySide6 import QtCore, QtWidgets

from gridironlabs.core.config import AppConfig
from gridironlabs.core.models import CoachSummary, PlayerSummary, TeamSummary
from gridironlabs.core.repository import SummaryRepository
from gridironlabs.services.search_service import SearchService
from gridironlabs.services.summary_service import SummaryService
from gridironlabs.ui.main_window import MainWindow, load_stylesheet


@dataclass
class InMemoryRepository(SummaryRepository):
    """
    Temporary in-memory repository seeded with placeholder data.
    Replace once Parquet datasets are wired in.
    """

    players_data: tuple[PlayerSummary, ...]
    teams_data: tuple[TeamSummary, ...]
    coaches_data: tuple[CoachSummary, ...]

    def players(self) -> Iterable[PlayerSummary]:
        return self.players_data

    def teams(self) -> Iterable[TeamSummary]:
        return self.teams_data

    def coaches(self) -> Iterable[CoachSummary]:
        return self.coaches_data


def _nflreadpy_missing() -> bool:
    return importlib.util.find_spec("nflreadpy") is None


def build_repository() -> SummaryRepository:
    players = (
        PlayerSummary(player_id="p1", name="Jane Doe", position="QB", team="NYG"),
        PlayerSummary(player_id="p2", name="John Smith", position="WR", team="KC"),
    )
    teams = (
        TeamSummary(team_id="t1", name="New York Giants", conference="NFC", division="East"),
        TeamSummary(team_id="t2", name="Kansas City Chiefs", conference="AFC", division="West"),
    )
    coaches = (
        CoachSummary(coach_id="c1", name="Alex Taylor", role="HC", team="NYG"),
        CoachSummary(coach_id="c2", name="Sam Jordan", role="OC", team="KC"),
    )
    return InMemoryRepository(players, teams, coaches)


def bootstrap(config: AppConfig, logger: logging.Logger) -> MainWindow:
    repository = build_repository()
    offline_mode = config.offline_mode or _nflreadpy_missing()
    if offline_mode:
        logger.info("Starting in offline placeholder mode (nflreadpy not available)")

    search_service = SearchService(repository, logger=logger)
    summary_service = SummaryService(repository)

    window = MainWindow(
        config=config,
        search_service=search_service,
        summary_service=summary_service,
        offline_mode=offline_mode,
        logger=logger,
    )

    stylesheet = load_stylesheet(config.paths.resources / "styles" / "dark.qss")
    if stylesheet:
        window.setStyleSheet(stylesheet)
    return window


def run(config: AppConfig, logger: logging.Logger) -> None:
    QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Gridiron Labs")
    app.setOrganizationName("Gridiron Labs")
    window = bootstrap(config, logger)
    window.show()
    app.exec()
