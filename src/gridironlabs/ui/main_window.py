"""Main window scaffold for the desktop UI."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Callable

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from gridironlabs.core.config import AppConfig, AppPaths
from gridironlabs.core.errors import DataValidationError, NotFoundError
from gridironlabs.core.models import GameSummary
from gridironlabs.data.repository import ParquetSummaryRepository
from gridironlabs import resources as package_resources
from gridironlabs.services.search import SearchService
from gridironlabs.services.summary import SummaryService
from gridironlabs.ui.pages.settings_page import SettingsPage
from gridironlabs.ui.pages.team_page import TeamSummaryPage
from gridironlabs.ui.pages.player_page import PlayerSummaryPage
from gridironlabs.ui.pages.base_page import BasePage
from gridironlabs.ui.panels import PanelChrome
from gridironlabs.ui.style.tokens import GRID
from gridironlabs.ui.widgets.navigation import NavigationBar
from gridironlabs.ui.widgets.standings import LeagueStandingsWidget, StandingsHeaderRow


class HomePage(BasePage):
    """Home page scaffold for panel experimentation."""

    def __init__(
        self, 
        title: str, 
        subtitle: str, 
        on_team_click: Callable[[str], None] | None = None,
        on_player_click: Callable[[str], None] | None = None
    ) -> None:
        super().__init__(cols=GRID.cols, rows=12)
        self.setObjectName("page-home")
        self._subtitle = subtitle
        self._on_team_click = on_team_click
        self._on_player_click = on_player_click

        # Minimal chrome box to start rebuilding the Home layout.
        self.league_standings_panel = PanelChrome(title="LEAGUE STANDINGS", panel_variant="table")
        
        # Configure the chrome to look like a full OOTP panel
        self.league_standings_panel.show_secondary_header(False)
        self.league_standings_panel.show_tertiary_header(True)
        self.league_standings_panel.set_footer_text("View: Standard Standings | 32 Teams")

        # Column headers (use a real layout so it aligns with row columns)
        self.league_standings_panel.header_tertiary.add_left(StandingsHeaderRow())

        # Content: Scrollable list of divisions
        self.standings_widget = LeagueStandingsWidget(on_team_click=self._on_team_click)
        self.league_standings_panel.set_body(self.standings_widget)

        # Dummy data
        self.standings_widget.add_division("AFC EAST", [
            ("1st", "Buffalo Bills", "11", "6", ".647", "-"),
            ("2nd", "Miami Dolphins", "9", "8", ".529", "2.0"),
            ("3rd", "New York Jets", "7", "10", ".412", "4.0"),
            ("4th", "New England Patriots", "4", "13", ".235", "7.0"),
        ])
        
        self.standings_widget.add_division("AFC NORTH", [
            ("1st", "Baltimore Ravens", "13", "4", ".765", "-"),
            ("2nd", "Cleveland Browns", "11", "6", ".647", "2.0"),
            ("3rd", "Pittsburgh Steelers", "10", "7", ".588", "3.0"),
            ("4th", "Cincinnati Bengals", "9", "8", ".529", "4.0"),
        ])
        
        self.standings_widget.add_division("AFC SOUTH", [
            ("1st", "Houston Texans", "10", "7", ".588", "-"),
            ("2nd", "Jacksonville Jaguars", "9", "8", ".529", "1.0"),
            ("3rd", "Indianapolis Colts", "9", "8", ".529", "1.0"),
            ("4th", "Tennessee Titans", "6", "11", ".353", "4.0"),
        ])

        self.standings_widget.add_division("AFC WEST", [
            ("1st", "Kansas City Chiefs", "12", "5", ".706", "-"),
            ("2nd", "Denver Broncos", "10", "7", ".588", "2.0"),
            ("3rd", "Las Vegas Raiders", "8", "9", ".471", "4.0"),
            ("4th", "Los Angeles Chargers", "7", "10", ".412", "5.0"),
        ])

        self.standings_widget.add_division("NFC EAST", [
            ("1st", "Dallas Cowboys", "12", "5", ".706", "-"),
            ("2nd", "Philadelphia Eagles", "11", "6", ".647", "1.0"),
            ("3rd", "New York Giants", "7", "10", ".412", "5.0"),
            ("4th", "Washington Commanders", "5", "12", ".294", "7.0"),
        ])

        self.standings_widget.add_division("NFC NORTH", [
            ("1st", "Green Bay Packers", "11", "6", ".647", "-"),
            ("2nd", "Minnesota Vikings", "10", "7", ".588", "1.0"),
            ("3rd", "Detroit Lions", "9", "8", ".529", "2.0"),
            ("4th", "Chicago Bears", "6", "11", ".353", "5.0"),
        ])

        self.standings_widget.add_division("NFC SOUTH", [
            ("1st", "New Orleans Saints", "10", "7", ".588", "-"),
            ("2nd", "Tampa Bay Buccaneers", "9", "8", ".529", "1.0"),
            ("3rd", "Atlanta Falcons", "8", "9", ".471", "2.0"),
            ("4th", "Carolina Panthers", "4", "13", ".235", "6.0"),
        ])

        self.standings_widget.add_division("NFC WEST", [
            ("1st", "San Francisco 49ers", "13", "4", ".765", "-"),
            ("2nd", "Seattle Seahawks", "10", "7", ".588", "3.0"),
            ("3rd", "Los Angeles Rams", "9", "8", ".529", "4.0"),
            ("4th", "Arizona Cardinals", "5", "12", ".294", "8.0"),
        ])

        # Extend to bottom of the page grid and reduce width by half.
        self.add_panel(self.league_standings_panel, col=0, row=0, col_span=13, row_span=12)

    def set_subtitle(self, text: str) -> None:
        self._subtitle = text


class SectionPage(QWidget):
    """Section page scaffold (content intentionally empty)."""

    def __init__(self, title: str, subtitle: str, *, show_states: bool = True) -> None:
        super().__init__()
        self.setObjectName(f"page-{title.lower().replace(' ', '-')}")

        layout = QVBoxLayout(self)
        # Match the top gap to the nav-context spacing.
        layout.setContentsMargins(16, 0, 16, 16)
        layout.setSpacing(12)
        self._subtitle = subtitle
        layout.addStretch(1)

    def set_subtitle(self, text: str) -> None:
        self._subtitle = text


class PageContextBar(QFrame):
    """Persistent context bar under the top navigation with per-page highlights."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PageContextBar")
        self.setFixedHeight(114)  # 2x the 57px nav height

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        self.icon_label = QLabel()
        self.icon_label.setObjectName("ContextBarIcon")
        self.icon_label.setFixedSize(56, 56)
        self.icon_label.setAlignment(Qt.AlignCenter)
        try:
            with package_resources.as_file("icons", "main_logo.png") as icon_path:
                pixmap = QPixmap(str(icon_path))
                if not pixmap.isNull():
                    self.icon_label.setPixmap(
                        pixmap.scaled(
                            self.icon_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                        )
                    )
        except FileNotFoundError:
            pass
        layout.addWidget(self.icon_label, 0, Qt.AlignVCenter)

        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(8)

        self.title_label = QLabel("Context")
        self.title_label.setObjectName("ContextBarTitle")
        self.subtitle_label = QLabel("Page-specific context will appear here.")
        self.subtitle_label.setObjectName("ContextBarSubtitle")
        self.subtitle_label.setWordWrap(True)

        content.addWidget(self.title_label)
        content.addWidget(self.subtitle_label)

        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(16)
        content.addLayout(self.stats_layout)
        content.addStretch(1)

        layout.addLayout(content)

    def set_content(self, *, title: str, subtitle: str, stats: Iterable[tuple[str, str]]) -> None:
        self.title_label.setText(title)
        self.subtitle_label.setText(subtitle)

        for idx in reversed(range(self.stats_layout.count())):
            item = self.stats_layout.takeAt(idx)
            if widget := item.widget():
                widget.setParent(None)

        for label_text, value_text in stats:
            stat = QFrame(self)
            stat.setObjectName("ContextBarStat")
            stat_layout = QVBoxLayout(stat)
            stat_layout.setContentsMargins(10, 8, 10, 8)
            stat_layout.setSpacing(2)

            value_label = QLabel(value_text)
            value_label.setObjectName("ContextBarStatValue")
            label_label = QLabel(label_text)
            label_label.setObjectName("ContextBarStatLabel")
            stat_layout.addWidget(value_label)
            stat_layout.addWidget(label_label)
            self.stats_layout.addWidget(stat)

        self.stats_layout.addStretch(1)


class SearchResultsPage(QWidget):
    """Search results page scaffold (content intentionally empty)."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("page-search")

        layout = QVBoxLayout(self)
        # Keep the vertical spacing consistent with the bar above.
        layout.setContentsMargins(16, 0, 16, 16)
        layout.setSpacing(12)
        layout.addStretch(1)

    def set_query(self, query: str) -> None:
        return

    def set_results(self, results: Iterable[Any]) -> None:  # noqa: ARG002 - placeholder hook
        return


class GridironLabsMainWindow(QMainWindow):
    """Main application shell with persistent navigation and stacked content."""

    def __init__(
        self, *, config: AppConfig, paths: AppPaths, logger: Any
    ) -> None:
        super().__init__()
        self.config = config
        self.paths = paths
        self.logger = logger
        self.repository: ParquetSummaryRepository | None = None
        self.search_service: SearchService | None = None
        self.summary_service: SummaryService | None = None

        self.setObjectName("GridironLabsMainWindow")
        self.setWindowTitle("Gridiron Labs")
        self.setMinimumSize(1100, 720)

        self.history: list[str] = []
        self.history_index = -1
        self.navigation_sections = ["home", "seasons", "teams", "players", "drafts", "history"]
        self.context_payloads = self._build_context_payloads(
            players=0, teams=0, coaches=0, seasons_span="No seasons detected"
        )
        self._matchup_strings: list[str] = []
        self._matchup_index = 0
        self._matchup_timer: QTimer | None = None

        container = QWidget(self)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(16)

        self.top_nav = NavigationBar(
            sections=[
                ("home", "HOME"),
                ("seasons", "SEASONS"),
                ("teams", "TEAMS"),
                ("players", "PLAYERS"),
                ("drafts", "DRAFTS"),
                ("history", "HISTORY"),
            ],
            on_home=self._on_home,
            on_section_selected=self._navigate_to,
            on_search=self._on_search,
            on_settings=self._on_settings,
            on_back=self._go_back,
            on_forward=self._go_forward,
            context_items=[
                "NFL Season",
                "Week 10",
                "Sun Nov 7th",
                "GB Packers (10-1) @ PIT Steelers (0-11)",
            ],
        )
        container_layout.addWidget(self.top_nav)

        self.context_bar = PageContextBar()
        container_layout.addWidget(self.context_bar)

        content_frame = QFrame(self)
        content_frame.setObjectName("ContentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(12, 0, 12, 12)
        content_layout.setSpacing(12)

        self.content_stack = QStackedWidget(self)
        self.content_stack.setObjectName("ContentStack")

        self.pages: dict[str, QWidget] = {}
        self._build_sections()

        self.settings_page = SettingsPage(config=self.config, paths=self.paths)
        self.content_stack.addWidget(self.settings_page)
        self.pages["settings"] = self.settings_page

        self.search_page = SearchResultsPage()
        self.content_stack.addWidget(self.search_page)
        self.pages["search"] = self.search_page

        self.team_summary_page = TeamSummaryPage()
        self.content_stack.addWidget(self.team_summary_page)
        self.pages["team-summary"] = self.team_summary_page

        self.player_summary_page = PlayerSummaryPage()
        self.content_stack.addWidget(self.player_summary_page)
        self.pages["player-summary"] = self.player_summary_page

        content_layout.addWidget(self.content_stack)
        container_layout.addWidget(content_frame)
        self.setCentralWidget(container)

        self._bootstrap_data()
        self._navigate_to("home")
        self._update_history_buttons()

    def _build_sections(self) -> None:
        definitions: dict[str, tuple[str, str]] = {
            "home": ("Home", "League dashboard placeholder with standings and leaders."),
            "seasons": ("Seasons", "Season timelines and summaries."),
            "teams": ("Teams", "Team pages with rosters and schedules."),
            "players": ("Players", "Player bios, ratings, and advanced metrics."),
            "drafts": ("Drafts", "Draft histories and pick outcomes."),
            "history": ("History", "Historic leaders and milestones."),
        }
        for key, (title, subtitle) in definitions.items():
            if key == "home":
                page = HomePage(
                    title, 
                    subtitle, 
                    on_team_click=self._on_team_selected,
                    on_player_click=self._on_player_selected
                )
            else:
                page = SectionPage(title, subtitle)
            page.setObjectName(f"page-{key}")
            self.pages[key] = page
            self.content_stack.addWidget(page)

    def _bootstrap_data(self) -> None:
        try:
            self.repository = ParquetSummaryRepository(
                self.paths.data_processed, schema_version=self.config.default_schema_version
            )
            players = list(self.repository.iter_players())
            teams = list(self.repository.iter_teams())
            coaches = list(self.repository.iter_coaches())
            games = list(self.repository.iter_games())

            self.summary_service = SummaryService(repository=self.repository)
            self.search_service = SearchService(repository=self.repository)
            self.search_service.build_index()

            seasons = {p.era for p in players if p.era} | {t.era for t in teams if t.era}
            season_span = (
                f"{min(seasons)}-{max(seasons)}" if seasons else "No seasons detected"
            )

            self._update_page_subtitles(players=players, teams=teams, coaches=coaches, seasons=season_span)
            matchups = self._build_upcoming_matchups(games, teams)
            self._start_matchup_cycle(matchups)
            self._refresh_context_payloads(
                players=len(players), teams=len(teams), coaches=len(coaches), seasons_span=season_span
            )
        except NotFoundError as exc:
            if self.logger:
                self.logger.warning("Data missing", extra={"error": str(exc)})
            self._refresh_context_payloads(players=0, teams=0, coaches=0, seasons_span="No seasons detected")
        except DataValidationError as exc:
            if self.logger:
                self.logger.error("Data validation failed", extra={"error": str(exc)})
            self._refresh_context_payloads(players=0, teams=0, coaches=0, seasons_span="Validation error")
        except Exception as exc:  # pragma: no cover - catch-all for UI bootstrap
            if self.logger:
                self.logger.exception("Unhandled data bootstrap failure", exc_info=exc)
            self._refresh_context_payloads(players=0, teams=0, coaches=0, seasons_span="Load failure")

    def _update_page_subtitles(
        self,
        *,
        players: list,
        teams: list,
        coaches: list,
        seasons: str,
    ) -> None:
        players_page = self.pages.get("players")
        teams_page = self.pages.get("teams")
        home_page = self.pages.get("home")
        seasons_page = self.pages.get("seasons")

        if players_page and hasattr(players_page, "set_subtitle"):
            players_page.set_subtitle(f"{len(players):,} players across {seasons}")
        if teams_page and hasattr(teams_page, "set_subtitle"):
            teams_page.set_subtitle(f"{len(teams):,} teams across {seasons}")
        if seasons_page and hasattr(seasons_page, "set_subtitle"):
            seasons_page.set_subtitle(f"Season span: {seasons}")
        if home_page and hasattr(home_page, "set_subtitle"):
            home_page.set_subtitle(
                f"{len(players):,} players | {len(teams):,} teams | {len(coaches):,} coaches"
            )

    def _build_context_payloads(
        self, *, players: int, teams: int, coaches: int, seasons_span: str
    ) -> dict[str, dict[str, str | list[tuple[str, str]]]]:
        return {
            "home": {
                "title": "League Overview",
                "subtitle": f"Seasons {seasons_span}",
                "stats": [
                    ("Players", f"{players:,}"),
                    ("Teams", f"{teams:,}"),
                    ("Coaches", f"{coaches:,}"),
                ],
            },
            "seasons": {
                "title": "Season Timeline",
                "subtitle": f"Season span: {seasons_span}",
                "stats": [("Players", f"{players:,}"), ("Teams", f"{teams:,}")],
            },
            "teams": {
                "title": "Teams Overview",
                "subtitle": "Rosters, schedules, and ratings",
                "stats": [("Teams", f"{teams:,}"), ("Players", f"{players:,}")],
            },
            "players": {
                "title": "Player Pool",
                "subtitle": f"{players:,} players across {seasons_span}",
                "stats": [("Players", f"{players:,}"), ("Coaches", f"{coaches:,}")],
            },
            "drafts": {
                "title": "Draft Histories",
                "subtitle": "Draft outcomes and pick values",
                "stats": [("Seasons", seasons_span), ("Teams", f"{teams:,}")],
            },
            "history": {
                "title": "Historic Leaders",
                "subtitle": "Milestones, records, and franchise lore",
                "stats": [("Players", f"{players:,}"), ("Teams", f"{teams:,}")],
            },
            "search": {
                "title": "Search",
                "subtitle": "Type a query and press Enter to search players, teams, and coaches.",
                "stats": [("Players indexed", f"{players:,}"), ("Teams indexed", f"{teams:,}")],
            },
            "settings": {
                "title": "Settings",
                "subtitle": "Runtime configuration overview",
                "stats": [
                    ("Environment", self.config.environment),
                    ("Schema", self.config.default_schema_version),
                    ("Theme", self.config.ui_theme),
                ],
            },
            "default": {
                "title": "Context",
                "subtitle": "Details will appear here.",
                "stats": [],
            },
        }

    def _refresh_context_payloads(
        self, *, players: int, teams: int, coaches: int, seasons_span: str
    ) -> None:
        self.context_payloads = self._build_context_payloads(
            players=players, teams=teams, coaches=coaches, seasons_span=seasons_span
        )
        current_section = self.history[self.history_index] if self.history_index >= 0 else "home"
        self._update_context_bar(current_section)

    def _update_context_bar(self, section_key: str) -> None:
        payload = self.context_payloads.get(section_key, self.context_payloads.get("default", {}))
        title = payload.get("title", "Context")
        subtitle = payload.get("subtitle", "")
        stats = payload.get("stats", [])
        self.context_bar.set_content(title=title, subtitle=subtitle, stats=stats)  # type: ignore[arg-type]

    def _navigate_to(self, section_key: str, *, from_history: bool = False) -> None:
        if section_key not in self.pages:
            return
        target = self.pages[section_key]
        self.content_stack.setCurrentWidget(target)
        if section_key in self.navigation_sections:
            self.top_nav.set_active(section_key)
        else:
            self.top_nav.clear_active()

        if not from_history:
            self._record_history(section_key)
        self._update_history_buttons()
        self._update_context_bar(section_key)

        if self.logger:
            self.logger.info("Navigate", extra={"section": section_key})

    def _record_history(self, section_key: str) -> None:
        if self.history and self.history[self.history_index] == section_key:
            return
        self.history = self.history[: self.history_index + 1]
        self.history.append(section_key)
        self.history_index = len(self.history) - 1

    def _update_history_buttons(self) -> None:
        self.top_nav.set_history_enabled(
            back_enabled=self.history_index > 0,
            forward_enabled=self.history_index < len(self.history) - 1,
        )

    def _go_back(self) -> None:
        if self.history_index <= 0:
            return
        self.history_index -= 1
        self._navigate_to(self.history[self.history_index], from_history=True)

    def _go_forward(self) -> None:
        if self.history_index >= len(self.history) - 1:
            return
        self.history_index += 1
        self._navigate_to(self.history[self.history_index], from_history=True)

    def _on_home(self) -> None:
        self._navigate_to("home")

    def _on_search(self, query: str) -> None:
        cleaned = query.strip()
        if self.logger:
            self.logger.info("Search submitted", extra={"query": cleaned})
        self.search_page.set_query(cleaned)
        if self.search_service:
            results = self.search_service.search(cleaned, limit=12)
            self.search_page.set_results(results)
        self._navigate_to("search")

    def _on_settings(self) -> None:
        if self.logger:
            self.logger.info("Settings opened")
        self._navigate_to("settings")

    def _on_team_selected(self, team_name: str) -> None:
        # Accept either full team name ("Kansas City Chiefs") or abbreviation ("KC").
        # Some UI surfaces may fall back to abbreviations if the team lookup is unavailable.
        resolved_name = team_name
        if self.repository:
            try:
                teams = list(self.repository.iter_teams())
                match = next(
                    (
                        t
                        for t in teams
                        if (t.name == team_name) or (t.team and t.team == team_name)
                    ),
                    None,
                )
                if match:
                    resolved_name = match.name
            except Exception:
                pass
        if self.logger:
            self.logger.info("Team selected", extra={"team": resolved_name, "raw_team": team_name})
        self.team_summary_page.set_team(resolved_name)
        self._navigate_to("team-summary")

    def _on_player_selected(self, player_name: str) -> None:
        if self.logger:
            self.logger.info("Player selected", extra={"player": player_name})
        self.player_summary_page.set_player(player_name)
        self._navigate_to("player-summary")

    def _build_upcoming_matchups(
        self, games: Iterable[GameSummary], teams: Iterable[Any]
    ) -> list[str]:
        games_list = list(games)
        if not games_list:
            return []

        latest_season = max(game.season for game in games_list)
        season_games = [g for g in games_list if g.season == latest_season]
        if not season_games:
            return []

        now = datetime.now()
        upcoming = [g for g in season_games if g.status != "final" or g.start_time >= now]
        if upcoming:
            future_weeks = [g.week for g in upcoming if g.start_time >= now]
            target_week = min(future_weeks) if future_weeks else min(g.week for g in upcoming)
        else:
            target_week = max(g.week for g in season_games)

        week_games = sorted(
            [g for g in season_games if g.week == target_week], key=lambda g: g.start_time
        )
        if not week_games:
            return []

        team_lookup: dict[str, str] = {}
        for team in teams:
            if getattr(team, "team", None):
                team_lookup[team.team] = team.name

        return [self._format_matchup(g, team_lookup) for g in week_games]

    def _format_matchup(self, game: GameSummary, team_lookup: dict[str, str]) -> str:
        day = game.start_time.day
        suffix = "th" if 10 <= day % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        date_str = f"{game.start_time.strftime('%a %b')} {day}{suffix}"
        home = team_lookup.get(game.home_team, game.home_team)
        away = team_lookup.get(game.away_team, game.away_team)
        return f"Week {game.week} {date_str} {away} @ {home}"

    def _start_matchup_cycle(self, matchups: list[str]) -> None:
        self._stop_matchup_cycle()
        self._matchup_strings = matchups
        self._matchup_index = 0
        if not matchups:
            return

        self.top_nav.set_context_items([self._matchup_strings[self._matchup_index]])
        if len(self._matchup_strings) == 1:
            return

        self._matchup_timer = QTimer(self)
        self._matchup_timer.setInterval(6000)
        self._matchup_timer.timeout.connect(self._advance_matchup)
        self._matchup_timer.start()

    def _advance_matchup(self) -> None:
        if not self._matchup_strings:
            return
        self._matchup_index = (self._matchup_index + 1) % len(self._matchup_strings)
        self.top_nav.set_context_items([self._matchup_strings[self._matchup_index]])

    def _stop_matchup_cycle(self) -> None:
        if self._matchup_timer:
            self._matchup_timer.stop()
            self._matchup_timer.deleteLater()
        self._matchup_timer = None
