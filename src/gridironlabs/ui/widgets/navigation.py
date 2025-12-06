"""Persistent navigation bar modeled after the OOTP-style top strip."""

from __future__ import annotations

from typing import Callable, Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStyle,
    QToolButton,
)


class NavigationBar(QFrame):
    """Top navigation bar with section buttons, context strip, search, and settings."""

    def __init__(
        self,
        *,
        sections: Iterable[tuple[str, str]],
        context_text: str,
        ticker_text: str,
        on_section_selected: Callable[[str], None],
        on_home: Callable[[], None],
        on_search: Callable[[str], None],
        on_settings: Callable[[], None] | None,
        on_back: Callable[[], None] | None = None,
        on_forward: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("TopNavigationBar")

        self._on_section_selected = on_section_selected
        self._on_home = on_home
        self._on_search = on_search
        self._on_settings = on_settings

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)

        self.back_button = self._icon_button(QStyle.SP_ArrowBack, "Back", on_back)
        self.forward_button = self._icon_button(QStyle.SP_ArrowForward, "Forward", on_forward)
        self.home_button = self._icon_button(QStyle.SP_DirHomeIcon, "Home", self._on_home)

        layout.addWidget(self.back_button)
        layout.addWidget(self.forward_button)
        layout.addWidget(self.home_button)

        self.section_group = QButtonGroup(self)
        self.section_group.setExclusive(True)
        self.section_buttons: dict[str, QPushButton] = {}
        for key, label in sections:
            button = QPushButton(label)
            button.setObjectName("NavSectionButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, key=key: self._handle_section(key))
            self.section_group.addButton(button)
            self.section_buttons[key] = button
            layout.addWidget(button)

        self.context_label = QLabel(context_text)
        self.context_label.setObjectName("ContextLabel")
        self.context_label.setAlignment(Qt.AlignVCenter)
        self.context_label.setMinimumWidth(240)
        layout.addWidget(self.context_label, 1)

        self.ticker_label = QLabel(ticker_text)
        self.ticker_label.setObjectName("TickerLabel")
        self.ticker_label.setAlignment(Qt.AlignVCenter)
        layout.addWidget(self.ticker_label, 0)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("TopNavSearch")
        self.search_input.setPlaceholderText("Search players, teams, coaches...")
        self.search_input.returnPressed.connect(self._emit_search)
        layout.addWidget(self.search_input, 0)

        self.settings_button = QPushButton("SETTINGS")
        self.settings_button.setObjectName("SettingsButton")
        self.settings_button.clicked.connect(lambda: self._on_settings() if self._on_settings else None)
        layout.addWidget(self.settings_button, 0)

    def _icon_button(
        self,
        icon: QStyle.StandardPixmap,
        tooltip: str,
        on_click: Callable[[], None] | None,
    ) -> QToolButton:
        button = QToolButton(self)
        button.setObjectName("NavIconButton")
        button.setIcon(self.style().standardIcon(icon))
        button.setToolTip(tooltip)
        button.setAutoRaise(True)
        button.setEnabled(on_click is not None)
        if on_click:
            button.clicked.connect(on_click)
        return button

    def _handle_section(self, key: str) -> None:
        self.set_active(key)
        self._on_section_selected(key)

    def _emit_search(self) -> None:
        self._on_search(self.search_input.text())

    def set_active(self, section_key: str) -> None:
        for key, button in self.section_buttons.items():
            button.setChecked(key == section_key)

    def clear_active(self) -> None:
        # Temporarily disable exclusivity to clear selections cleanly.
        self.section_group.setExclusive(False)
        for button in self.section_buttons.values():
            button.setChecked(False)
        self.section_group.setExclusive(True)

    def set_history_enabled(self, *, back_enabled: bool, forward_enabled: bool) -> None:
        self.back_button.setEnabled(back_enabled)
        self.forward_button.setEnabled(forward_enabled)
