 from __future__ import annotations
 
from functools import partial

from PySide6 import QtCore, QtWidgets


class NavigationBar(QtWidgets.QFrame):
    """
    Top navigation bar inspired by the OOTP-style layout.
    """

    back_requested = QtCore.Signal()
    forward_requested = QtCore.Signal()
    home_requested = QtCore.Signal()
    navigate_requested = QtCore.Signal(str)
    search_requested = QtCore.Signal(str)
    settings_requested = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.section_buttons: dict[str, QtWidgets.QPushButton] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("topNav")
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        self.back_button = QtWidgets.QToolButton()
        self.back_button.setObjectName("navBack")
        self.back_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowBack))
        self.back_button.setAutoRaise(True)

        self.forward_button = QtWidgets.QToolButton()
        self.forward_button.setObjectName("navForward")
        self.forward_button.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowForward)
        )
        self.forward_button.setAutoRaise(True)

        self.home_button = QtWidgets.QToolButton()
        self.home_button.setObjectName("navHome")
        self.home_button.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DirHomeIcon)
        )
        self.home_button.setAutoRaise(True)

        layout.addWidget(self.back_button)
        layout.addWidget(self.forward_button)
        layout.addWidget(self.home_button)

        self.section_group = QtWidgets.QButtonGroup(self)
        self.section_group.setExclusive(True)

        for name, label in [
            ("seasons", "SEASONS"),
            ("teams", "TEAMS"),
            ("players", "PLAYERS"),
            ("drafts", "DRAFTS"),
            ("history", "HISTORY"),
        ]:
            button = QtWidgets.QPushButton(label)
            button.setObjectName(f"nav-{name}")
            button.setCheckable(True)
            button.clicked.connect(partial(self._emit_navigation, name))
            self.section_group.addButton(button)
            self.section_buttons[name] = button
            layout.addWidget(button)

        layout.addSpacing(8)

        context_container = QtWidgets.QWidget(self)
        context_layout = QtWidgets.QVBoxLayout(context_container)
        context_layout.setContentsMargins(0, 0, 0, 0)
        context_layout.setSpacing(2)

        self.context_label = QtWidgets.QLabel("NFL Season | Week 10")
        self.context_label.setObjectName("contextLabel")
        self.ticker_label = QtWidgets.QLabel("GB Packers (10-1) @ PIT Steelers (0-11)")
        self.ticker_label.setObjectName("tickerLabel")

        context_layout.addWidget(self.context_label)
        context_layout.addWidget(self.ticker_label)
        layout.addWidget(context_container, 1)

        self.search_field = QtWidgets.QLineEdit()
        self.search_field.setObjectName("navSearch")
        self.search_field.setPlaceholderText("Search players, teams, coaches")
        self.search_field.returnPressed.connect(self._emit_search)

        self.settings_button = QtWidgets.QPushButton("SETTINGS")
        self.settings_button.setObjectName("navSettings")
        self.settings_button.clicked.connect(self.settings_requested.emit)

        layout.addWidget(self.search_field, 0)
        layout.addWidget(self.settings_button)

        self.back_button.clicked.connect(self.back_requested.emit)
        self.forward_button.clicked.connect(self.forward_requested.emit)
        self.home_button.clicked.connect(self.home_requested.emit)

    def set_active_section(self, name: str) -> None:
        if name == "home":
            self.section_group.setExclusive(False)
            for button in self.section_buttons.values():
                button.setChecked(False)
            self.section_group.setExclusive(True)
            return
        button = self.section_buttons.get(name)
        if button:
            button.setChecked(True)

    def set_history_enabled(self, back_enabled: bool, forward_enabled: bool) -> None:
        self.back_button.setEnabled(back_enabled)
        self.forward_button.setEnabled(forward_enabled)

    @QtCore.Slot()
    def _emit_search(self) -> None:
        self.search_requested.emit(self.search_field.text())

    @QtCore.Slot(str)
    def _emit_navigation(self, name: str) -> None:
        self.navigate_requested.emit(name)
