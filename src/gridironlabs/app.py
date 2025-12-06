 from __future__ import annotations
 
 from dataclasses import dataclass
 
 from PySide6 import QtWidgets
 
 from gridironlabs.core.config import AppConfig, load_config
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
 
     def players(self):
         return self.players_data
 
     def teams(self):
         return self.teams_data
 
     def coaches(self):
         return self.coaches_data
 
 
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
 
def bootstrap(config: AppConfig) -> MainWindow:
    repository = build_repository()
    search_service = SearchService(repository)
    _ = SummaryService(repository)

    window = MainWindow(search_service=search_service)

    stylesheet = load_stylesheet(config.paths.resources / "styles" / "dark.qss")
    if stylesheet:
        window.setStyleSheet(stylesheet)
    return window
 
 
 def run() -> None:
     config = load_config()
     app = QtWidgets.QApplication([])
     window = bootstrap(config)
     window.show()
     app.exec()
