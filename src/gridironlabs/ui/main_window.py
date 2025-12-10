"""Main window scaffold for the desktop UI."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QColorDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSlider,
    QSpinBox,
    QTextEdit,
    QSizePolicy,
    QStackedWidget,
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
    """Lightweight painted toggle to mimic the design reference."""

    def __init__(self, checked: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.setText("")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._track_height = 20
        self._track_width = 42
        self._margin = 3
        self.setFixedSize(self._track_width + self._margin * 2, self._track_height + self._margin * 2)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        track_rect = QRectF(
            self._margin,
            (self.height() - self._track_height) / 2,
            self._track_width,
            self._track_height,
        )

        base_color = QColor("#3b3f4a")
        active_color = QColor("#2563eb")
        disabled_color = QColor("#2a2d35")
        thumb_color = QColor("#f9fafb")
        thumb_disabled = QColor("#6b7280")

        track_color = active_color if self.isChecked() else base_color
        if not self.isEnabled():
            track_color = disabled_color

        painter.setPen(Qt.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(track_rect, self._track_height / 2, self._track_height / 2)

        thumb_diameter = self._track_height
        thumb_x = track_rect.x() + (self._track_width - thumb_diameter) if self.isChecked() else track_rect.x()
        thumb_rect = QRectF(thumb_x, track_rect.y(), thumb_diameter, thumb_diameter)
        painter.setBrush(thumb_color if self.isEnabled() else thumb_disabled)
        painter.drawEllipse(thumb_rect)


class SettingsPage(QWidget):
    """Read-only settings overview until editable preferences land."""

    def __init__(self, config: AppConfig, paths: AppPaths) -> None:
        super().__init__()
        self.setObjectName("page-settings")
        self.config = config
        self.paths = paths

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self._generate_players_checkbox: QCheckBox | None = None
        self._player_scope_checkboxes: list[QCheckBox] = []

        title_label = QLabel("GridironLabs Settings")
        title_label.setObjectName("PageTitle")
        layout.addWidget(title_label)
        subtitle_label = QLabel("Static UI mock for upcoming Settings experience.")
        subtitle_label.setObjectName("PageSubtitle")
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)

        canvas = QHBoxLayout()
        canvas.setSpacing(12)

        data_panel = self._build_data_generation_panel()
        grid_panel = self._build_grid_layout_panel()
        test_panel = self._build_test_cases_panel()
        debug_panel = self._build_debug_output_panel()

        middle_column = QVBoxLayout()
        middle_column.setSpacing(12)
        middle_column.addWidget(grid_panel, 1)
        middle_column.addWidget(test_panel, 1)

        canvas.addWidget(data_panel, 4)
        canvas.addLayout(middle_column, 3)
        canvas.addWidget(debug_panel, 3)

        layout.addLayout(canvas, 1)
        layout.addStretch(1)

    def _build_data_generation_panel(self) -> QFrame:
        frame = QFrame(self)
        frame.setObjectName("SettingsPanel")
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QLabel("Data Generation")
        header.setObjectName("SettingsSectionTitle")
        layout.addWidget(header)

        body = QHBoxLayout()
        body.setSpacing(12)
        layout.addLayout(body, 1)

        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        body.addLayout(left_col, 1)

        left_col.addLayout(self._season_range_row())
        for label in ["Real Data", "Pull NFLverse", "Pull Pro-Football-Reference"]:
            row, _ = self._switch_row(label)
            left_col.addLayout(row)

        generation_box, generation_checks = self._checklist_box(
            title="Generation Targets",
            options=["Generate Teams", "Generate Coaches", "Generate Players"],
        )
        self._generate_players_checkbox = generation_checks[-1]
        left_col.addWidget(generation_box)

        players_box, player_checks = self._checklist_box(
            title="Player Scope",
            options=["Offense", "Defense", "Special Teams"],
            enabled=False,
        )
        self._player_scope_checkboxes = player_checks
        if self._generate_players_checkbox:
            self._generate_players_checkbox.toggled.connect(
                lambda checked: self._toggle_player_scope(checked)
            )
            self._generate_players_checkbox.setChecked(False)
            self._toggle_player_scope(False)
        left_col.addWidget(players_box)
        left_col.addStretch(1)

        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        body.addLayout(right_col, 1)
        right_col.addWidget(self._build_last_update_box(), 1)

        generate_button = QPushButton("Generate Data")
        generate_button.setObjectName("PrimaryButton")
        generate_button.setMinimumHeight(38)
        generate_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(generate_button)

        return frame

    def _season_range_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        label = QLabel("Season Range")
        label.setObjectName("SettingsLabel")
        row.addWidget(label)

        start_combo = self._year_combo(1999)
        end_combo = self._year_combo(1999, default=datetime.now().year)
        row.addStretch(1)
        row.addWidget(start_combo)
        row.addWidget(end_combo)
        return row

    def _year_combo(self, start_year: int, default: int | None = None) -> QComboBox:
        combo = QComboBox()
        combo.setObjectName("SettingsCombo")
        current_year = datetime.now().year
        for year in range(start_year, current_year + 1):
            combo.addItem(str(year))
        if default:
            combo.setCurrentText(str(default))
        else:
            combo.setCurrentIndex(0)
        return combo

    def _switch_row(self, label_text: str, *, checked: bool = False) -> tuple[QHBoxLayout, ToggleSwitch]:
        row = QHBoxLayout()
        row.setSpacing(8)
        label = QLabel(label_text)
        label.setObjectName("SettingsLabel")
        row.addWidget(label)
        row.addStretch(1)
        toggle = ToggleSwitch(checked)
        row.addWidget(toggle)
        return row, toggle

    def _checklist_box(
        self, *, title: str, options: list[str], enabled: bool = True
    ) -> tuple[QFrame, list[QCheckBox]]:
        frame = QFrame(self)
        frame.setObjectName("SettingsGroup")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        header = QLabel(title)
        header.setObjectName("SettingsSubheader")
        layout.addWidget(header)

        checkboxes: list[QCheckBox] = []
        for option in options:
            box = QCheckBox(option)
            box.setObjectName("SettingsCheckbox")
            box.setChecked(enabled)
            box.setEnabled(enabled)
            layout.addWidget(box)
            checkboxes.append(box)

        return frame, checkboxes

    def _toggle_player_scope(self, enabled: bool) -> None:
        for box in self._player_scope_checkboxes:
            box.setEnabled(enabled)
            if not enabled:
                box.setChecked(False)

    def _build_last_update_box(self) -> QFrame:
        frame = QFrame(self)
        frame.setObjectName("SettingsGroup")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        header_row = QHBoxLayout()
        header_row.setSpacing(6)
        data_label = QLabel("Data Type")
        data_label.setObjectName("SettingsSubheader")
        last_update_label = QLabel("Last Update")
        last_update_label.setObjectName("SettingsSubheader")
        header_row.addWidget(data_label)
        header_row.addStretch(1)
        header_row.addWidget(last_update_label)
        layout.addLayout(header_row)

        entries = [
            ("Teams", "Dec 7th, 2025 @ 12:02pm"),
            ("Coaches", "Dec 7th, 2025 @ 12:02pm"),
            ("Players", "Dec 7th, 2025 @ 12:02pm"),
            ("Offense", "Dec 7th, 2025 @ 12:02pm"),
            ("Defense", "Dec 7th, 2025 @ 12:02pm"),
            ("Spec Teams", "Dec 7th, 2025 @ 12:02pm"),
        ]
        for label_text, value_text in entries:
            row = QHBoxLayout()
            row.setSpacing(6)
            label = QLabel(label_text)
            label.setObjectName("SettingsLabel")
            value = QLabel(value_text)
            value.setObjectName("SettingsLabel")
            row.addWidget(label)
            row.addStretch(1)
            row.addWidget(value)
            layout.addLayout(row)

        layout.addStretch(1)

        total_row = QHBoxLayout()
        total_row.setSpacing(6)
        total_label = QLabel("Total Data Size")
        total_label.setObjectName("SettingsSubheader")
        total_value = QLabel("35GB")
        total_value.setObjectName("SettingsLabel")
        total_row.addWidget(total_label)
        total_row.addStretch(1)
        total_row.addWidget(total_value)
        layout.addLayout(total_row)
        return frame

    def _build_grid_layout_panel(self) -> QFrame:
        frame = QFrame(self)
        frame.setObjectName("SettingsPanel")
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QLabel("UI Grid Layout")
        header.setObjectName("SettingsSectionTitle")
        layout.addWidget(header)

        enable_row, _ = self._switch_row("Enable Grid", checked=True)
        layout.addLayout(enable_row)

        opacity_row = QHBoxLayout()
        opacity_row.setSpacing(8)
        opacity_label = QLabel("Opacity")
        opacity_label.setObjectName("SettingsLabel")
        opacity_row.addWidget(opacity_label)
        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(70)
        opacity_slider.setObjectName("SettingsSlider")
        opacity_value = QLabel("70%")
        opacity_value.setObjectName("SettingsLabel")
        opacity_slider.valueChanged.connect(lambda val: opacity_value.setText(f"{val}%"))
        opacity_row.addWidget(opacity_slider, 1)
        opacity_row.addWidget(opacity_value)
        layout.addLayout(opacity_row)

        color_row = QHBoxLayout()
        color_row.setSpacing(8)
        color_label = QLabel("Color")
        color_label.setObjectName("SettingsLabel")
        color_row.addWidget(color_label)

        color_button = QPushButton()
        color_button.setObjectName("ColorSwatch")
        color_button.setFixedSize(32, 24)
        self._set_swatch_color(color_button, "#CD4D4D")

        color_input = QLineEdit("#CD4D4D")
        color_input.setObjectName("HexInput")
        color_input.setMaxLength(7)
        color_input.returnPressed.connect(
            lambda: self._apply_hex_input(color_input, color_button)
        )
        color_button.clicked.connect(
            lambda: self._open_color_dialog(color_button, color_input)
        )
        color_row.addStretch(1)
        color_row.addWidget(color_button)
        color_row.addWidget(color_input)
        layout.addLayout(color_row)

        cell_row = QHBoxLayout()
        cell_row.setSpacing(8)
        cell_label = QLabel("Cell Size")
        cell_label.setObjectName("SettingsLabel")
        cell_row.addWidget(cell_label)
        cell_row.addStretch(1)
        cell_size = QSpinBox()
        cell_size.setObjectName("SettingsSpin")
        cell_size.setMinimum(1)
        cell_size.setMaximum(24)
        cell_size.setValue(1)
        cell_size.setSuffix(" px")
        cell_row.addWidget(cell_size)
        layout.addLayout(cell_row)
        layout.addStretch(1)
        return frame

    def _set_swatch_color(self, button: QPushButton, color_hex: str) -> None:
        button.setStyleSheet(
            f"QPushButton#ColorSwatch {{ background-color: {color_hex}; border: 1px solid #2d313d; border-radius: 4px; }}"
        )
        button.setProperty("color_hex", color_hex)

    def _apply_hex_input(self, line_edit: QLineEdit, button: QPushButton) -> None:
        text = line_edit.text().strip()
        color = QColor(text)
        if color.isValid():
            normalized = color.name(QColor.HexRgb)
            self._set_swatch_color(button, normalized)
            line_edit.setText(normalized)

    def _open_color_dialog(self, button: QPushButton, line_edit: QLineEdit) -> None:
        initial = QColor(button.property("color_hex") or "#CD4D4D")
        color = QColorDialog.getColor(initial, self, "Select Grid Color")
        if color.isValid():
            normalized = color.name(QColor.HexRgb)
            self._set_swatch_color(button, normalized)
            line_edit.setText(normalized)

    def _build_test_cases_panel(self) -> QFrame:
        frame = QFrame(self)
        frame.setObjectName("SettingsPanel")
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QLabel("Test Cases")
        header.setObjectName("SettingsSectionTitle")
        layout.addWidget(header)

        for label_text in ["Test 1", "Test 2", "Test 3"]:
            row, _ = self._switch_row(label_text, checked=True)
            layout.addLayout(row)

        layout.addStretch(1)
        actions = QHBoxLayout()
        actions.addStretch(1)
        execute_button = QPushButton("Execute Tests")
        execute_button.setObjectName("PrimaryButton")
        execute_button.setMinimumHeight(34)
        actions.addWidget(execute_button)
        layout.addLayout(actions)
        return frame

    def _build_debug_output_panel(self) -> QFrame:
        frame = QFrame(self)
        frame.setObjectName("SettingsPanel")
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        header = QLabel("Debug Output")
        header.setObjectName("SettingsSectionTitle")
        layout.addWidget(header)

        console = QTextEdit()
        console.setObjectName("DebugConsole")
        console.setReadOnly(True)
        console.setLineWrapMode(QTextEdit.NoWrap)
        console.setText(
            "> Executing \"Test 1\"...\n"
            "\"Test 1\" passed!\n"
            "> Executing \"Test 2\"...\n"
            "\"Test 2\" failed...\n"
            "> Executing \"Test 3\"..."
        )
        layout.addWidget(console, 1)
        return frame



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
