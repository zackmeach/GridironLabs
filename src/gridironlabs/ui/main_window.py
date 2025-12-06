"""Main window scaffold for the desktop UI."""

from __future__ import annotations

from typing import Any

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
from gridironlabs.ui.widgets.navigation import NavigationBar
from gridironlabs.ui.widgets.state_panels import (
    EmptyPanel,
    ErrorPanel,
    LoadingPanel,
    StatusBanner,
)


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
        placeholders.addWidget(
            EmptyPanel("Results will appear here once data is wired to services.")
        )
        placeholders.addStretch(1)
        layout.addLayout(placeholders)
        layout.addStretch(1)

    def set_query(self, query: str) -> None:
        if query:
            self.summary_label.setText(f'Showing placeholder results for "{query}".')
        else:
            self.summary_label.setText("Type a query and press Enter.")


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

        self.setObjectName("GridironLabsMainWindow")
        self.setWindowTitle("Gridiron Labs")
        self.setMinimumSize(1100, 720)

        self.history: list[str] = []
        self.history_index = -1
        self.navigation_sections = ["home", "seasons", "teams", "players", "drafts", "history"]

        container = QWidget(self)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.top_nav = NavigationBar(
            sections=[
                ("home", "HOME"),
                ("seasons", "SEASONS"),
                ("teams", "TEAMS"),
                ("players", "PLAYERS"),
                ("drafts", "DRAFTS"),
                ("history", "HISTORY"),
            ],
            context_text="NFL Season | Week 10 | GB Packers (10-1) @ PIT Steelers (0-11)",
            ticker_text="What's happening",
            on_home=self._on_home,
            on_section_selected=self._navigate_to,
            on_search=self._on_search,
            on_settings=self._on_settings,
            on_back=self._go_back,
            on_forward=self._go_forward,
        )
        container_layout.addWidget(self.top_nav)

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

        self.search_page = SearchResultsPage()
        self.content_stack.addWidget(self.search_page)
        self.pages["search"] = self.search_page

        content_layout.addWidget(self.content_stack)
        container_layout.addWidget(content_frame)
        self.setCentralWidget(container)

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
            page = SectionPage(title, subtitle)
            page.setObjectName(f"page-{key}")
            self.pages[key] = page
            self.content_stack.addWidget(page)

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
        self._navigate_to("search")

    def _on_settings(self) -> None:
        if self.logger:
            self.logger.info("Settings clicked (placeholder)")
