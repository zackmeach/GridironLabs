 from __future__ import annotations
 
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from PySide6 import QtCore, QtWidgets

from gridironlabs.core import AppConfig
from gridironlabs.services.search_service import SearchService
from gridironlabs.services.summary_service import SummaryService
from gridironlabs.ui.widgets.navigation_bar import NavigationBar
from gridironlabs.ui.widgets.placeholders import InfoBanner, StatePlaceholder


class MainWindow(QtWidgets.QMainWindow):
    """
    Application shell with persistent top navigation bar and stacked views.
    """

    def __init__(
        self,
        config: AppConfig,
        search_service: SearchService,
        summary_service: SummaryService,
        offline_mode: bool = False,
        logger: Optional[logging.Logger] = None,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.config = config
        self.search_service = search_service
        self.summary_service = summary_service
        self.offline_mode = offline_mode
        self.logger = logger

        self.pages: Dict[str, QtWidgets.QWidget] = {}
        self.history: List[str] = []
        self.future: List[str] = []
        self.current_page: str = "home"

        self.setWindowTitle("Gridiron Labs")
        self.resize(1280, 800)
        self.setObjectName("mainWindow")
        self._build_ui()
        self._wire_signals()
        self._show_page("home", record_history=False)

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget(self)
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.nav_bar = NavigationBar(self)
        main_layout.addWidget(self.nav_bar)

        if self.offline_mode:
            self.offline_banner = InfoBanner(
                "Offline placeholder mode: install nflreadpy to enable live data pulls."
            )
            main_layout.addWidget(self.offline_banner)

        content_frame = QtWidgets.QFrame(self)
        content_layout = QtWidgets.QVBoxLayout(content_frame)
        content_layout.setContentsMargins(16, 12, 16, 16)
        content_layout.setSpacing(12)

        self.stack = QtWidgets.QStackedWidget(self)
        self.stack.setObjectName("contentStack")
        content_layout.addWidget(self.stack, 1)

        main_layout.addWidget(content_frame, 1)
        self.setCentralWidget(central)

        self._register_pages()

    def _register_pages(self) -> None:
        self.pages["home"] = self._build_home_page()
        self.pages["seasons"] = self._build_section_page(
            "Seasons",
            "Season timelines, standings, and schedules will appear here.",
            state="loading",
        )
        self.pages["teams"] = self._build_section_page(
            "Teams",
            "Browse divisions, conferences, and roster summaries.",
            state="empty",
        )
        self.pages["players"] = self._build_section_page(
            "Players",
            "Player cards, ratings, and comparisons will load here.",
            state="loading",
        )
        self.pages["drafts"] = self._build_section_page(
            "Drafts",
            "Historical and upcoming draft classes with pick value charts.",
            state="empty",
        )
        self.pages["history"] = self._build_section_page(
            "History",
            "Franchise records, coaching trees, and milestones will land here.",
            state="error",
        )
        self.pages["search"] = self._build_search_page()

        for widget in self.pages.values():
            self.stack.addWidget(widget)

    def _wire_signals(self) -> None:
        self.nav_bar.navigate_requested.connect(self._on_navigate)
        self.nav_bar.home_requested.connect(self._navigate_home)
        self.nav_bar.search_requested.connect(self._on_search)
        self.nav_bar.back_requested.connect(self._go_back)
        self.nav_bar.forward_requested.connect(self._go_forward)
        self.nav_bar.settings_requested.connect(self._on_settings)

    def _build_home_page(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget(self)
        widget.setObjectName("homePage")
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        hero = QtWidgets.QLabel("Gridiron Labs")
        hero.setObjectName("heroTitle")
        hero.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        subtitle = QtWidgets.QLabel("OOTP26-inspired NFL analytics explorer")
        subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("heroSubtitle")

        placeholder = StatePlaceholder(
            "Start exploring",
            "Use the top navigation to jump into seasons, teams, players, and more.",
            state="info",
        )

        layout.addSpacing(12)
        layout.addStretch()
        layout.addWidget(hero)
        layout.addWidget(subtitle)
        layout.addWidget(placeholder, 1)
        layout.addStretch()
        return widget

    def _build_section_page(self, title: str, description: str, state: str) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget(self)
        widget.setObjectName(f"{title.lower()}Page")
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        header = QtWidgets.QLabel(title.upper())
        header.setObjectName("pageHeader")
        layout.addWidget(header)

        placeholder = StatePlaceholder(title, description, state=state)
        layout.addWidget(placeholder, 1)
        return widget

    def _build_search_page(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget(self)
        widget.setObjectName("searchPage")
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.search_heading = QtWidgets.QLabel("Search Results")
        self.search_heading.setObjectName("pageHeader")
        layout.addWidget(self.search_heading)

        self.search_results = QtWidgets.QListWidget()
        self.search_results.setObjectName("searchResultsList")
        self.search_placeholder = StatePlaceholder(
            "Waiting for a query", "Type a search above to preview matches.", state="info"
        )
        layout.addWidget(self.search_results)
        layout.addWidget(self.search_placeholder)
        self._toggle_search_placeholder(show_placeholder=True)
        return widget

    def _toggle_search_placeholder(self, show_placeholder: bool) -> None:
        self.search_results.setVisible(not show_placeholder)
        self.search_placeholder.setVisible(show_placeholder)

    @QtCore.Slot()
    def _navigate_home(self) -> None:
        self._show_page("home")

    @QtCore.Slot(str)
    def _on_navigate(self, page: str) -> None:
        self._show_page(page)

    @QtCore.Slot()
    def _go_back(self) -> None:
        if not self.history:
            return
        previous = self.history.pop()
        self.future.append(self.current_page)
        self._show_page(previous, record_history=False)

    @QtCore.Slot()
    def _go_forward(self) -> None:
        if not self.future:
            return
        target = self.future.pop()
        self.history.append(self.current_page)
        self._show_page(target, record_history=False)

    def _show_page(self, name: str, record_history: bool = True) -> None:
        if name not in self.pages:
            return
        if record_history and self.current_page != name:
            self.history.append(self.current_page)
            self.future.clear()
        self.current_page = name
        self.stack.setCurrentWidget(self.pages[name])
        self.nav_bar.set_active_section(name)
        self.nav_bar.set_history_enabled(bool(self.history), bool(self.future))

    @QtCore.Slot(str)
    def _on_search(self, query: str) -> None:
        cleaned = query.strip()
        if not cleaned:
            return
        results = self.search_service.search(cleaned)
        self._render_search_results(cleaned, results)
        self._show_page("search")
        if self.logger:
            self.logger.info(
                "search submitted",
                extra={"correlation_id": "search", "query": cleaned, "result_count": len(results)},
            )

    def _render_search_results(self, query: str, results: Iterable) -> None:
        self.search_heading.setText(f"Search Results — “{query}”")
        self.search_results.clear()
        for result in results:
            item = QtWidgets.QListWidgetItem(f"{result.entity_type.title()}: {result.name}")
            self.search_results.addItem(item)
        self._toggle_search_placeholder(show_placeholder=self.search_results.count() == 0)

    @QtCore.Slot()
    def _on_settings(self) -> None:
        QtWidgets.QMessageBox.information(self, "Settings", "Settings panel coming soon.")


def load_stylesheet(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
