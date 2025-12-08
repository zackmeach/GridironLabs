"""Persistent navigation bar modeled after the OOTP-style top strip."""

from __future__ import annotations

from typing import Callable, Iterable

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QStyle,
    QToolButton,
    QWidget,
)


class NavigationBar(QFrame):
    """Top navigation bar with section buttons, context strip, search, and settings."""

    def __init__(
        self,
        *,
        sections: Iterable[tuple[str, str]],
        on_section_selected: Callable[[str], None],
        on_home: Callable[[], None],
        on_search: Callable[[str], None],
        on_settings: Callable[[], None] | None,
        on_back: Callable[[], None] | None = None,
        on_forward: Callable[[], None] | None = None,
        context_items: Iterable[str] = (),
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
        layout.addWidget(self.home_button)
        layout.addWidget(self.forward_button)

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

        reference_height = next(iter(self.section_buttons.values()), None)
        self._context_height = reference_height.sizeHint().height() if reference_height else 42

        self.context_strip = self._build_context_strip(context_items)
        layout.addWidget(self.context_strip, 0)
        layout.setAlignment(self.context_strip, Qt.AlignVCenter)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("TopNavSearch")
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumWidth(320)
        self.search_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        search_icon = self.style().standardIcon(QStyle.SP_FileDialogContentsView)
        self.search_input.addAction(search_icon, QLineEdit.LeadingPosition)
        self.search_input.returnPressed.connect(self._emit_search)
        layout.addWidget(self.search_input, 2)

        self.settings_button = QPushButton("SETTINGS")
        self.settings_button.setObjectName("SettingsButton")
        self.settings_button.clicked.connect(lambda: self._on_settings() if self._on_settings else None)
        layout.addWidget(self.settings_button, 0)

        # Make the bar 1.5x taller than its natural hint for better touch targets.
        self.setFixedHeight(57)

    def _icon_button(
        self,
        icon: QStyle.StandardPixmap,
        tooltip: str,
        on_click: Callable[[], None] | None,
    ) -> QToolButton:
        button = QToolButton(self)
        button.setObjectName("NavIconButton")
        button.setIcon(self._tinted_icon(icon))
        button.setToolTip(tooltip)
        button.setAutoRaise(True)
        button.setEnabled(on_click is not None)
        if on_click:
            button.clicked.connect(on_click)
        return button

    def _tinted_icon(self, icon: QStyle.StandardPixmap) -> QIcon:
        base_icon = self.style().standardIcon(icon)
        size = 24

        def make_pix(color: QColor, mode: QIcon.Mode) -> QPixmap:
            pix = base_icon.pixmap(size, size, mode)
            if pix.isNull():
                return pix
            tinted = QPixmap(pix.size())
            tinted.fill(Qt.transparent)
            painter = QPainter(tinted)
            painter.drawPixmap(0, 0, pix)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(tinted.rect(), color)
            painter.end()
            return tinted

        icon_out = QIcon()
        icon_out.addPixmap(make_pix(QColor("#ffffff"), QIcon.Mode.Normal), QIcon.Mode.Normal)
        icon_out.addPixmap(make_pix(QColor("#4b5563"), QIcon.Mode.Disabled), QIcon.Mode.Disabled)
        return icon_out

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

    def set_context_items(self, items: Iterable[str]) -> None:
        # Clear existing
        for idx in reversed(range(self.context_layout.count())):
            item = self.context_layout.takeAt(idx)
            if widget := item.widget():
                widget.setParent(None)
        for text in items:
            label = QLabel(text)
            label.setObjectName("ContextLabel")
            self.context_layout.addWidget(label)
        self.context_layout.addStretch(1)

    def _build_context_strip(self, items: Iterable[str]) -> QWidget:
        strip = QFrame()
        strip.setObjectName("ContextStrip")
        self.context_layout = QHBoxLayout(strip)
        self.context_layout.setContentsMargins(8, 0, 8, 0)
        self.context_layout.setSpacing(12)
        strip.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        strip.setFixedWidth(520)
        strip.setFixedHeight(self._context_height)
        for text in items:
            label = QLabel(text)
            label.setObjectName("ContextLabel")
            self.context_layout.addWidget(label)
        self.context_layout.addStretch(1)
        return strip