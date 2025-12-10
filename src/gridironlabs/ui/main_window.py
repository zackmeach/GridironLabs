"""Main window scaffold for the desktop UI."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QColorDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)

from gridironlabs.core.config import AppConfig, AppPaths
from gridironlabs.core.errors import DataValidationError, NotFoundError
from gridironlabs.core.models import GameSummary, SearchResult
from gridironlabs.data.repository import ParquetSummaryRepository
from gridironlabs.data.schemas import SCHEMA_REGISTRY
from gridironlabs.services.search import SearchService
from gridironlabs.services.summary import SummaryService
from gridironlabs.ui.widgets.navigation import NavigationBar
from gridironlabs.ui.widgets.league_leaders import (
    LeaderboardData,
    LeadersPanel,
    build_leaderboard,
)
from gridironlabs.ui.widgets.state_panels import (
    EmptyPanel,
    ErrorPanel,
    LoadingPanel,
    StatusBanner,
)


class HomePage(QWidget):
    """Home dashboard with league leaders grid."""

    def __init__(self, title: str, subtitle: str) -> None:
        super().__init__()
        self.setObjectName("page-home")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("PageSubtitle")
        subtitle_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)

        self.leaders_panel = LeadersPanel()
        layout.addWidget(self.leaders_panel)
        layout.addStretch(1)

        self.subtitle_label = subtitle_label

    def set_subtitle(self, text: str) -> None:
        self.subtitle_label.setText(text)

    def set_leaders(self, data: LeaderboardData | None) -> None:
        if data is None:
            data = LeaderboardData(groups=())
        self.leaders_panel.set_data(data)


class SectionPage(QWidget):
    """Simple placeholder page with reusable state panels."""

    def __init__(self, title: str, subtitle: str, *, show_states: bool = True) -> None:
        super().__init__()
        self.setObjectName(f"page-{title.lower().replace(' ', '-')}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("PageSubtitle")
        subtitle_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        self.subtitle_label = subtitle_label

        if show_states:
            states_row = QHBoxLayout()
            states_row.setSpacing(10)
            states_row.addWidget(LoadingPanel("Loading stub content..."))
            states_row.addWidget(EmptyPanel("No data yet. Connect to processed Parquet."))
            states_row.addWidget(ErrorPanel("Errors will surface here."))
            states_row.addStretch(1)
            layout.addLayout(states_row)

        layout.addStretch(1)

    def set_subtitle(self, text: str) -> None:
        self.subtitle_label.setText(text)


class PageContextBar(QFrame):
    """Persistent context bar under the top navigation with per-page highlights."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PageContextBar")
        self.setMinimumHeight(75)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        self.title_label = QLabel("Context")
        self.title_label.setObjectName("ContextBarTitle")
        self.subtitle_label = QLabel("Page-specific context will appear here.")
        self.subtitle_label.setObjectName("ContextBarSubtitle")
        self.subtitle_label.setWordWrap(True)

        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)

        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(16)
        layout.addLayout(self.stats_layout)
        layout.addStretch(1)

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


class SettingsPage(QWidget):
    """Read-only settings overview until editable preferences land."""

    def __init__(self, config: AppConfig, paths: AppPaths) -> None:
        super().__init__()
        self.setObjectName("page-settings")
        self.config = config
        self.paths = paths
        self.current_color = "#CD4D4D"
        self.player_category_checks: list[QCheckBox] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title_label = QLabel("GridironLabs Settings")
        title_label.setObjectName("PageTitle")
        subtitle_label = QLabel(
            "Work-in-progress settings layout. Controls are cosmetic while the data "
            "layer is still being wired up."
        )
        subtitle_label.setObjectName("PageSubtitle")
        subtitle_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)

        main_row = QHBoxLayout()
        main_row.setSpacing(12)
        layout.addLayout(main_row)

        data_panel, data_layout = self._build_panel("Data Generation")
        data_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_row.addWidget(data_panel, 4)

        center_column = QVBoxLayout()
        center_column.setSpacing(12)
        main_row.addLayout(center_column, 3)

        debug_panel, debug_layout = self._build_panel("Debug Output")
        debug_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_row.addWidget(debug_panel, 3)

        self._build_data_generation(data_layout)
        self._build_ui_grid(center_column)
        self._build_test_cases(center_column)
        self._build_debug_output(debug_layout)

        layout.addStretch(1)

    def _build_panel(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        panel = QFrame(self)
        panel.setObjectName("SettingsPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(12, 12, 12, 12)
        panel_layout.setSpacing(10)

        header = QLabel(title)
        header.setObjectName("SettingsPanelTitle")
        panel_layout.addWidget(header)
        return panel, panel_layout

    def _build_group_box(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        box = QFrame(self)
        box.setObjectName("SettingsGroup")
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(10, 10, 10, 10)
        box_layout.setSpacing(6)

        label = QLabel(title)
        label.setObjectName("SettingsGroupLabel")
        box_layout.addWidget(label)
        return box, box_layout

    def _build_data_generation(self, panel_layout: QVBoxLayout) -> None:
        columns = QHBoxLayout()
        columns.setSpacing(12)
        panel_layout.addLayout(columns)

        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        columns.addLayout(left_col, 1)

        right_col = QVBoxLayout()
        right_col.setSpacing(10)
        columns.addLayout(right_col, 1)

        season_row = QHBoxLayout()
        season_row.setSpacing(8)
        season_label = QLabel("Season Range")
        season_label.setObjectName("SettingsRowLabel")
        season_row.addWidget(season_label)
        season_row.addStretch(1)

        years = [str(year) for year in range(1999, datetime.now().year + 1)]
        self.start_year = QComboBox()
        self.start_year.setObjectName("SettingsCombo")
        self.start_year.addItems(years)
        self.start_year.setCurrentText("1999")

        self.end_year = QComboBox()
        self.end_year.setObjectName("SettingsCombo")
        self.end_year.addItems(years)
        self.end_year.setCurrentText(str(datetime.now().year))

        season_row.addWidget(self.start_year)
        season_row.addWidget(self.end_year)
        left_col.addLayout(season_row)

        switches_box, switches_layout = self._build_group_box("Sources")
        self._add_toggle_row(switches_layout, "Real Data", checked=True)
        self._add_toggle_row(switches_layout, "Pull NFLverse", checked=True)
        self._add_toggle_row(switches_layout, "Pull Pro-Football-Reference", checked=True)
        left_col.addWidget(switches_box)

        generate_box, generate_layout = self._build_group_box("Generate")
        self._add_checkbox(generate_layout, "Generate Teams")
        self._add_checkbox(generate_layout, "Generate Coaches")
        generate_players = self._add_checkbox(generate_layout, "Generate Players")
        generate_players.setChecked(True)
        left_col.addWidget(generate_box)

        players_box, players_layout = self._build_group_box("Players")
        for label in ("Offense", "Defense", "Special Teams"):
            cb = self._add_checkbox(players_layout, label)
            self.player_category_checks.append(cb)
        left_col.addWidget(players_box)

        generate_players.stateChanged.connect(self._on_generate_players_changed)
        self._on_generate_players_changed(Qt.Checked)
        left_col.addStretch(1)

        updates_box, updates_layout = self._build_group_box("Last Update")
        updates_grid = QGridLayout()
        updates_grid.setHorizontalSpacing(10)
        updates_grid.setVerticalSpacing(6)

        updates_grid.addWidget(QLabel("Data Type"), 0, 0)
        updates_grid.addWidget(QLabel("Last Update"), 0, 1)

        timestamp = self._format_timestamp(datetime.now())
        for idx, label in enumerate(
            ("Teams", "Coaches", "Players", "Offense", "Defense", "Spec Teams"), start=1
        ):
            updates_grid.addWidget(QLabel(label), idx, 0)
            updates_grid.addWidget(QLabel(timestamp), idx, 1)

        updates_layout.addLayout(updates_grid)

        total_row = QHBoxLayout()
        total_row.setSpacing(8)
        total_label = QLabel("Total Data Size")
        total_label.setObjectName("SettingsRowLabel")
        total_value = QLabel("35GB")
        total_value.setObjectName("SettingsValueLabel")
        total_row.addWidget(total_label)
        total_row.addStretch(1)
        total_row.addWidget(total_value)
        updates_layout.addLayout(total_row)

        right_col.addWidget(updates_box)

        generate_button = QPushButton("Generate Data")
        generate_button.setObjectName("PrimaryButton")
        generate_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        right_col.addWidget(generate_button)
        right_col.addStretch(1)

    def _build_ui_grid(self, column_layout: QVBoxLayout) -> None:
        panel, panel_layout = self._build_panel("UI Grid Layout")
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        column_layout.addWidget(panel, 1)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)
        panel_layout.addLayout(form_layout)

        self._add_toggle_row(form_layout, "Enable Grid", checked=True)

        opacity_row = QHBoxLayout()
        opacity_row.setSpacing(8)
        opacity_label = QLabel("Opacity")
        opacity_label.setObjectName("SettingsRowLabel")
        opacity_row.addWidget(opacity_label)
        opacity_row.addStretch(1)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setObjectName("SettingsSlider")
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(60)
        self.opacity_slider.setSingleStep(5)
        self.opacity_value = QLabel("60%")
        self.opacity_value.setObjectName("SettingsValueLabel")
        self.opacity_slider.valueChanged.connect(
            lambda value: self.opacity_value.setText(f"{value}%")
        )
        opacity_row.addWidget(self.opacity_slider)
        opacity_row.addWidget(self.opacity_value)
        form_layout.addLayout(opacity_row)

        color_row = QHBoxLayout()
        color_row.setSpacing(8)
        color_label = QLabel("Color")
        color_label.setObjectName("SettingsRowLabel")
        color_row.addWidget(color_label)
        color_row.addStretch(1)

        self.color_swatch = QPushButton()
        self.color_swatch.setObjectName("ColorSwatch")
        self.color_swatch.setFixedSize(38, 24)
        self.color_swatch.clicked.connect(self._open_color_dialog)

        self.color_input = QLineEdit(self.current_color)
        self.color_input.setObjectName("HexInput")
        self.color_input.setMaxLength(7)
        self.color_input.setPlaceholderText("#CD4D4D")
        self.color_input.returnPressed.connect(self._handle_hex_input)

        color_row.addWidget(self.color_swatch)
        color_row.addWidget(self.color_input)
        form_layout.addLayout(color_row)
        self._apply_color(QColor(self.current_color))

        cell_row = QHBoxLayout()
        cell_row.setSpacing(8)
        cell_label = QLabel("Cell Size")
        cell_label.setObjectName("SettingsRowLabel")
        cell_row.addWidget(cell_label)
        cell_row.addStretch(1)

        self.cell_size = QSpinBox()
        self.cell_size.setObjectName("CellSizeSpin")
        self.cell_size.setRange(1, 64)
        self.cell_size.setValue(1)
        self.cell_size.setSuffix(" px")
        cell_row.addWidget(self.cell_size)
        form_layout.addLayout(cell_row)

        panel_layout.addStretch(1)

    def _build_test_cases(self, column_layout: QVBoxLayout) -> None:
        panel, panel_layout = self._build_panel("Test Cases")
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        column_layout.addWidget(panel, 1)

        toggles_layout = QVBoxLayout()
        toggles_layout.setSpacing(8)
        panel_layout.addLayout(toggles_layout)

        self._add_toggle_row(toggles_layout, "Test 1", checked=True)
        self._add_toggle_row(toggles_layout, "Test 2", checked=True)
        self._add_toggle_row(toggles_layout, "Test 3", checked=True)

        action_row = QHBoxLayout()
        action_row.addStretch(1)
        execute_button = QPushButton("Execute Tests")
        execute_button.setObjectName("PrimaryButton")
        execute_button.setFixedHeight(32)
        action_row.addWidget(execute_button)
        panel_layout.addLayout(action_row)

    def _build_debug_output(self, panel_layout: QVBoxLayout) -> None:
        debug_output = QPlainTextEdit()
        debug_output.setObjectName("DebugOutput")
        debug_output.setReadOnly(True)
        debug_output.setPlainText(self._demo_debug_text())
        panel_layout.addWidget(debug_output)
        panel_layout.addStretch(1)

    def _add_toggle_row(
        self, parent_layout: QVBoxLayout, label_text: str, *, checked: bool = False
    ) -> QCheckBox:
        row = QHBoxLayout()
        row.setSpacing(8)
        label = QLabel(label_text)
        label.setObjectName("SettingsRowLabel")
        toggle = QCheckBox()
        toggle.setObjectName("ToggleSwitch")
        toggle.setChecked(checked)

        row.addWidget(label)
        row.addStretch(1)
        row.addWidget(toggle)
        parent_layout.addLayout(row)
        return toggle

    def _add_checkbox(self, parent_layout: QVBoxLayout, label_text: str) -> QCheckBox:
        checkbox = QCheckBox(label_text)
        checkbox.setObjectName("SettingsCheckbox")
        parent_layout.addWidget(checkbox)
        return checkbox

    def _on_generate_players_changed(self, state: int) -> None:
        enabled = state == Qt.Checked
        for checkbox in self.player_category_checks:
            checkbox.setEnabled(enabled)
            if not enabled:
                checkbox.setChecked(False)

    def _apply_color(self, color: QColor) -> None:
        if not color.isValid():
            return
        self.current_color = color.name().upper()
        self.color_input.setText(self.current_color)
        self.color_swatch.setStyleSheet(
            f"#ColorSwatch {{ background-color: {self.current_color}; border: 1px solid #3b4252; border-radius: 4px; }}"
        )

    def _open_color_dialog(self) -> None:
        chosen = QColorDialog.getColor(QColor(self.current_color), self, "Choose Grid Color")
        if chosen.isValid():
            self._apply_color(chosen)

    def _handle_hex_input(self) -> None:
        candidate = self.color_input.text().strip()
        if not candidate.startswith("#"):
            candidate = f"#{candidate}"
        color = QColor(candidate)
        if color.isValid():
            self._apply_color(color)
        else:
            self.color_input.setText(self.current_color)

    @staticmethod
    def _format_timestamp(dt: datetime) -> str:
        suffix = "th" if 10 <= dt.day % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(dt.day % 10, "th")
        timestamp = dt.strftime(f"%b {dt.day}{suffix}, %Y @ %I:%M%p")
        return timestamp.replace("AM", "am").replace("PM", "pm")

    @staticmethod
    def _demo_debug_text() -> str:
        return (
            '> Executing "Test 1"...\n'
            '"Test 1" passed!\n'
            '> Executing "Test 2"...\n'
            '"Test 2" failed...\n'
            '> Executing "Test 3"...'
        )


class SearchResultsPage(QWidget):
    """Placeholder search results view triggered from the top nav."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("page-search")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title_label = QLabel("Search Results")
        title_label.setObjectName("PageTitle")
        self.summary_label = QLabel("Type a query and press Enter.")
        self.summary_label.setObjectName("PageSubtitle")
        self.summary_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(self.summary_label)

        placeholders = QHBoxLayout()
        placeholders.setSpacing(10)
        self.results_layout = QVBoxLayout()
        self.results_layout.setSpacing(6)
        placeholders.addLayout(self.results_layout, 3)
        placeholders.addStretch(1)
        layout.addLayout(placeholders)
        layout.addStretch(1)

    def set_query(self, query: str) -> None:
        if query:
            self.summary_label.setText(f'Showing results for "{query}".')
        else:
            self.summary_label.setText("Type a query and press Enter.")

    def set_results(self, results: Iterable[SearchResult]) -> None:
        for idx in reversed(range(self.results_layout.count())):
            item = self.results_layout.takeAt(idx)
            if widget := item.widget():
                widget.setParent(None)

        results = list(results)
        if not results:
            self.results_layout.addWidget(EmptyPanel("No matches yet."))
            return

        for hit in results:
            label = QLabel(
                f"{hit.entity_type.title()}: {hit.label} "
                f"{'(team: ' + hit.context.get('team', '') + ')' if hit.context else ''}"
            )
            label.setObjectName("SearchResultRow")
            self.results_layout.addWidget(label)
        self.results_layout.addStretch(1)


class GridironLabsMainWindow(QMainWindow):
    """Main application shell with persistent navigation and stacked content."""

    def __init__(
        self, *, config: AppConfig, paths: AppPaths, logger: Any, offline_mode: bool = False
    ) -> None:
        super().__init__()
        self.config = config
        self.paths = paths
        self.logger = logger
        self.offline_mode = offline_mode
        self.repository: ParquetSummaryRepository | None = None
        self.search_service: SearchService | None = None
        self.summary_service: SummaryService | None = None

        self.setObjectName("GridironLabsMainWindow")
        self.setWindowTitle("Gridiron Labs")
        self.setMinimumSize(1100, 720)

        self.history: list[str] = []
        self.history_index = -1
        self.navigation_sections = ["home", "seasons", "teams", "players", "drafts", "history"]
        self.home_page: HomePage | None = None
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

        if offline_mode:
            container_layout.addWidget(
                StatusBanner(
                    "Offline placeholder mode: nflreadpy not installed. Data-backed views are stubbed.",
                    severity="offline",
                )
            )

        content_frame = QFrame(self)
        content_frame.setObjectName("ContentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(12, 12, 12, 12)
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

        content_layout.addWidget(self.content_stack)
        container_layout.addWidget(content_frame)
        self.setCentralWidget(container)

        self._bootstrap_data(container_layout)
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
                page = HomePage(title, subtitle)
                self.home_page = page
            else:
                page = SectionPage(title, subtitle)
            page.setObjectName(f"page-{key}")
            self.pages[key] = page
            self.content_stack.addWidget(page)

    def _bootstrap_data(self, container_layout: QVBoxLayout) -> None:
        try:
            schema_key = f"players:{self.config.default_schema_version}"
            schema_version = SCHEMA_REGISTRY.get(schema_key, SCHEMA_REGISTRY["players:v0"])
            self.repository = ParquetSummaryRepository(self.paths.data_processed, schema_version)
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
            if self.home_page:
                leaderboard = build_leaderboard(players)
                self.home_page.set_leaders(leaderboard)
            matchups = self._build_upcoming_matchups(games, teams)
            self._start_matchup_cycle(matchups)
            self._refresh_context_payloads(
                players=len(players), teams=len(teams), coaches=len(coaches), seasons_span=season_span
            )
        except NotFoundError as exc:
            container_layout.insertWidget(
                1,
                StatusBanner(
                    f"Processed data missing at {self.paths.data_processed}. "
                    "Run scripts/generate_fake_nfl_data.py to bootstrap.",
                    severity="offline",
                ),
            )
            if self.logger:
                self.logger.warning("Data missing", extra={"error": str(exc)})
            self._refresh_context_payloads(players=0, teams=0, coaches=0, seasons_span="No seasons detected")
        except DataValidationError as exc:
            container_layout.insertWidget(
                1,
                StatusBanner(
                    f"Data validation issue: {exc}",
                    severity="error",
                ),
            )
            if self.logger:
                self.logger.error("Data validation failed", extra={"error": str(exc)})
            self._refresh_context_payloads(players=0, teams=0, coaches=0, seasons_span="Validation error")
        except Exception as exc:  # pragma: no cover - catch-all for UI bootstrap
            container_layout.insertWidget(
                1,
                StatusBanner(
                    "Failed to load processed data. See logs for details.",
                    severity="error",
                ),
            )
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
