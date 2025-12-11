"""Main window scaffold for the desktop UI."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from PySide6.QtCore import Qt, QTimer, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSlider,
    QSpinBox,
    QSizePolicy,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
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


class ToggleSwitch(QCheckBox):
    """Lightweight painted toggle for cosmetic on/off controls."""

    def __init__(self, checked: bool = False) -> None:
        super().__init__()
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("ToggleSwitch")
        self.setFixedHeight(26)

    def sizeHint(self) -> QSize:  # pragma: no cover - trivial UI
        return QSize(46, 28)

    def paintEvent(self, event) -> None:  # pragma: no cover - trivial UI
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        track_rect = QRect(0, (self.height() - 22) // 2, 46, 22)
        track_color = QColor("#7c3aed") if self.isChecked() else QColor("#1f2933")
        if not self.isEnabled():
            track_color = QColor("#111827")
        painter.setPen(Qt.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(track_rect, 11, 11)

        thumb_color = QColor("#f9fafc") if self.isEnabled() else QColor("#6b7280")
        thumb_diameter = 16
        thumb_x = track_rect.left() + 4 if not self.isChecked() else track_rect.right() - thumb_diameter - 3
        thumb_rect = QRect(thumb_x, track_rect.top() + 3, thumb_diameter, thumb_diameter)
        painter.setBrush(thumb_color)
        painter.drawEllipse(thumb_rect)
        painter.end()


class SettingsPage(QWidget):
    """Cosmetic settings layout mirroring the shared mock."""

    def __init__(self, config: AppConfig, paths: AppPaths) -> None:
        super().__init__()
        self.setObjectName("page-settings")
        self.config = config
        self.paths = paths

        self.player_option_checkboxes: list[QCheckBox] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addLayout(self._build_header(paths))
        layout.addLayout(self._build_content_grid())
        layout.addStretch(1)

    def _build_header(self, paths: AppPaths) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(10)

        logo = QLabel()
        logo.setObjectName("SettingsLogo")
        icon_path = Path(__file__).resolve().parent.parent / "resources" / "icons" / "main_logo.png"
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            if not pixmap.isNull():
                logo.setPixmap(pixmap.scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setFixedSize(60, 60)
        logo.setAlignment(Qt.AlignCenter)

        title = QLabel("GridironLabs Settings")
        title.setObjectName("SettingsHeading")

        header.addWidget(logo, 0, Qt.AlignLeft | Qt.AlignVCenter)
        header.addWidget(title, 0, Qt.AlignLeft | Qt.AlignVCenter)
        header.addStretch(1)
        return header

    def _build_content_grid(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        data_card = self._build_data_generation_card()
        data_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        row.addWidget(data_card, 4)

        middle_container = QWidget()
        middle_layout = QVBoxLayout(middle_container)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(12)

        ui_grid = self._build_ui_grid_card()
        ui_grid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        middle_layout.addWidget(ui_grid, 1)

        test_cases = self._build_test_cases_card()
        test_cases.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        middle_layout.addWidget(test_cases, 1)

        row.addWidget(middle_container, 3)

        debug_card = self._build_debug_output_card()
        debug_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        row.addWidget(debug_card, 3)

        return row

    def _build_data_generation_card(self) -> QFrame:
        card, layout = self._card("Data Generation")

        content = QHBoxLayout()
        content.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(10)
        left.addLayout(self._build_season_range_row())
        left.addLayout(self._build_switch_row("Real Data", checked=True))
        left.addLayout(self._build_switch_row("Pull NFLverse", checked=True))
        left.addLayout(self._build_switch_row("Pull Pro-Football-Reference", checked=True))

        generate_group, generate_checkboxes = self._checkbox_group(
            "Generate Data", ["Generate Teams", "Generate Coaches", "Generate Players"]
        )
        player_types_group, player_checkboxes = self._checkbox_group(
            "Player Types", ["Offense", "Defense", "Special Teams"]
        )
        self.player_option_checkboxes = player_checkboxes
        if generate_checkboxes:
            generate_checkboxes[-1].toggled.connect(self._set_player_option_enabled)
            self._set_player_option_enabled(generate_checkboxes[-1].isChecked())

        left.addWidget(generate_group)
        left.addWidget(player_types_group)
        left.addStretch(1)

        right = QVBoxLayout()
        right.setSpacing(8)
        right.addWidget(self._build_last_update_table())
        right.addLayout(self._build_total_row("Total Data Size", "35GB"))

        generate_button = QPushButton("Generate Data")
        generate_button.setObjectName("PrimaryButton")
        generate_button.setMinimumHeight(40)
        generate_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        right.addWidget(generate_button)

        content.addLayout(left, 1)
        content.addLayout(right, 1)
        layout.addLayout(content)
        return card

    def _build_ui_grid_card(self) -> QFrame:
        card, layout = self._card("UI Grid Layout")
        layout.addLayout(self._build_switch_row("Enable Grid", checked=True))
        layout.addLayout(self._build_opacity_row())
        layout.addLayout(self._build_color_row())
        layout.addLayout(self._build_cell_size_row())
        layout.addStretch(1)
        return card

    def _build_test_cases_card(self) -> QFrame:
        card, layout = self._card("Test Cases")
        layout.addLayout(self._build_switch_row("Test 1", checked=True))
        layout.addLayout(self._build_switch_row("Test 2", checked=True))
        layout.addLayout(self._build_switch_row("Test 3", checked=True))

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        execute_button = QPushButton("Execute Tests")
        execute_button.setObjectName("GhostButton")
        execute_button.setMinimumHeight(36)
        button_row.addWidget(execute_button, 0, Qt.AlignRight)
        layout.addLayout(button_row)
        return card

    def _build_debug_output_card(self) -> QFrame:
        card, layout = self._card("Debug Output")
        terminal = QTextEdit()
        terminal.setObjectName("TerminalOutput")
        terminal.setReadOnly(True)
        terminal.setText(
            '> Executing "Test 1"...\n'
            '"Test 1" passed!\n'
            '> Executing "Test 2"...\n'
            '"Test 2" failed...\n'
            '> Executing "Test 3"...'
        )
        layout.addWidget(terminal)
        return card

    def _build_header_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SettingsLabel")
        return label

    def _build_switch_row(self, text: str, *, checked: bool = False) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(self._build_header_label(text))
        row.addStretch(1)
        row.addWidget(ToggleSwitch(checked))
        return row

    def _build_opacity_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(self._build_header_label("Opacity"))
        slider = QSlider(Qt.Horizontal)
        slider.setObjectName("SettingsSlider")
        slider.setRange(0, 100)
        slider.setValue(60)
        value_label = QLabel(f"{slider.value()}%")
        value_label.setObjectName("SettingsLabel")
        slider.valueChanged.connect(lambda value: value_label.setText(f"{value}%"))
        row.addWidget(slider, 1)
        row.addWidget(value_label)
        return row

    def _build_color_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(self._build_header_label("Color"))
        swatch = QFrame()
        swatch.setObjectName("ColorSwatch")
        swatch.setFixedSize(42, 26)
        swatch.setStyleSheet("background-color: #cd4d4d;")
        row.addWidget(swatch, 0, Qt.AlignLeft)

        input_hex = QLineEdit("#CD4D4D")
        input_hex.setObjectName("SettingsInput")
        input_hex.setMaxLength(7)
        input_hex.setFixedWidth(110)
        input_hex.returnPressed.connect(
            lambda: self._apply_hex_color(swatch, input_hex)
        )
        row.addWidget(input_hex)
        row.addStretch(1)
        return row

    def _build_cell_size_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(self._build_header_label("Cell Size"))
        spin = QSpinBox()
        spin.setObjectName("SettingsSpinBox")
        spin.setRange(1, 50)
        spin.setValue(1)
        spin.setSuffix(" px")
        spin.setFixedWidth(90)
        row.addWidget(spin)
        row.addStretch(1)
        return row

    def _build_season_range_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(self._build_header_label("Season Range"))
        start = self._year_combo(default=1999)
        end = self._year_combo(default=datetime.now().year)
        row.addWidget(start)
        row.addWidget(end)
        row.addStretch(1)
        return row

    def _build_last_update_table(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("SettingsSubCard")
        grid = QFormLayout(frame)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setSpacing(6)

        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        data_label = QLabel("Data Type")
        data_label.setObjectName("SettingsTableHeader")
        last_label = QLabel("Last Update")
        last_label.setObjectName("SettingsTableHeader")
        header_row.addWidget(data_label, 1)
        header_row.addWidget(last_label, 1)
        grid.addRow(header_row)

        now_text = self._timestamp_text()
        for data_type in ("Teams", "Coaches", "Players", "Offense", "Defense", "Spec Teams"):
            row = QHBoxLayout()
            row.setSpacing(8)
            label = QLabel(data_type)
            label.setObjectName("SettingsTableCell")
            stamp = QLabel(now_text)
            stamp.setObjectName("SettingsTableCell")
            row.addWidget(label, 1)
            row.addWidget(stamp, 1)
            grid.addRow(row)
        return frame

    def _build_total_row(self, label_text: str, value_text: str) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        label = QLabel(label_text)
        label.setObjectName("SettingsCaption")
        value = QLabel(value_text)
        value.setObjectName("SettingsLabel")
        row.addWidget(label)
        row.addStretch(1)
        row.addWidget(value, 0, Qt.AlignRight)
        return row

    def _year_combo(self, *, default: int) -> QComboBox:
        combo = QComboBox()
        combo.setObjectName("SettingsCombo")
        current_year = datetime.now().year
        for year in range(1999, current_year + 1):
            combo.addItem(str(year))
        combo.setCurrentText(str(default))
        combo.setFixedWidth(96)
        return combo

    def _checkbox_group(self, title: str, items: Iterable[str]) -> tuple[QFrame, list[QCheckBox]]:
        frame = QFrame()
        frame.setObjectName("SettingsSubCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        header = QLabel(title)
        header.setObjectName("SettingsLabel")
        layout.addWidget(header)

        checkboxes: list[QCheckBox] = []
        for item in items:
            cb = QCheckBox(item)
            cb.setChecked(True)
            cb.setObjectName("SettingsCheckbox")
            layout.addWidget(cb)
            checkboxes.append(cb)
        return frame, checkboxes

    def _card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName("SettingsCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("SettingsCardTitle")
        layout.addWidget(title_label)
        return frame, layout

    def _timestamp_text(self) -> str:
        return datetime.now().strftime("%b %d, %Y @ %I:%M%p").lower()

    def _set_player_option_enabled(self, enabled: bool) -> None:
        for checkbox in self.player_option_checkboxes:
            checkbox.setEnabled(enabled)

    def _apply_hex_color(self, swatch: QFrame, line_edit: QLineEdit) -> None:
        value = self._normalize_hex(line_edit.text())
        swatch.setStyleSheet(f"background-color: {value};")
        line_edit.setText(value.upper())

    @staticmethod
    def _normalize_hex(text: str) -> str:
        value = text.strip().lstrip("#")
        if len(value) not in (3, 6) or any(ch not in "0123456789abcdefABCDEF" for ch in value):
            return "#cd4d4d"
        if len(value) == 3:
            value = "".join(ch * 2 for ch in value)
        return f"#{value.lower()}"


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
