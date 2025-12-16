"""Panel card chrome.

A `PanelCard` provides consistent "OOTP-like" panel styling:

- optional header (title left, actions right)
- thin separator under the header
- body container with consistent padding

Panel content should be placed inside `body_layout`.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget

from gridironlabs.ui.style.tokens import SPACING
from gridironlabs.ui.widgets.base_components import TitleLabel


class PanelCard(QFrame):
    """Reusable panel card shell with header + body."""

    def __init__(
        self,
        title: str | None = None,
        *,
        header_actions: QWidget | None = None,
        show_header: bool = True,
        show_separator: bool = True,
        margins: tuple[int, int, int, int] = SPACING.panel_padding,
        spacing: int = SPACING.panel_spacing,
        title_object_name: str = "CardTitlePrimary",
    ) -> None:
        super().__init__()

        self.setObjectName("PanelCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._header_enabled = bool(show_header)
        self._separator_enabled = bool(show_separator)

        root = QVBoxLayout(self)
        root.setContentsMargins(*margins)
        root.setSpacing(spacing)

        self._header_row = QWidget(self)
        self._header_row.setObjectName("PanelCardHeader")
        header_layout = QHBoxLayout(self._header_row)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        self.title_label = TitleLabel("", object_name=title_object_name)
        header_layout.addWidget(self.title_label, 0, Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addStretch(1)

        self._actions_host = QWidget(self._header_row)
        self._actions_host.setObjectName("PanelCardHeaderActions")
        self._actions_layout = QHBoxLayout(self._actions_host)
        self._actions_layout.setContentsMargins(0, 0, 0, 0)
        self._actions_layout.setSpacing(8)
        header_layout.addWidget(self._actions_host, 0, Qt.AlignRight | Qt.AlignVCenter)

        root.addWidget(self._header_row)

        self._separator = QFrame(self)
        self._separator.setObjectName("PanelCardSeparator")
        self._separator.setFrameShape(QFrame.HLine)
        self._separator.setFrameShadow(QFrame.Plain)
        self._separator.setLineWidth(1)
        root.addWidget(self._separator)

        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(spacing)
        root.addLayout(self.body_layout)

        self.set_title(title)
        self.set_header_actions(header_actions)
        self._sync_header_visibility()

    def set_title(self, title: str | None) -> None:
        """Update the header title."""

        if title is None or not str(title).strip():
            self.title_label.setText("")
            self.title_label.setVisible(False)
        else:
            self.title_label.setText(str(title))
            self.title_label.setVisible(True)

        self._sync_header_visibility()

    def set_header_actions(self, widget: QWidget | None) -> None:
        """Replace the header-right actions widget."""

        while self._actions_layout.count():
            item = self._actions_layout.takeAt(0)
            if w := item.widget():
                w.setParent(None)

        if widget is not None:
            widget.setParent(self._actions_host)
            self._actions_layout.addWidget(widget)

        self._sync_header_visibility()

    def set_header_visible(self, visible: bool) -> None:
        self._header_enabled = bool(visible)
        self._sync_header_visibility()

    def set_separator_visible(self, visible: bool) -> None:
        self._separator_enabled = bool(visible)
        self._sync_header_visibility()

    def set_body(self, widget: QWidget) -> None:
        """Replace the body contents with a single widget."""

        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            if w := item.widget():
                w.setParent(None)

        widget.setParent(self)
        self.body_layout.addWidget(widget)

    def _sync_header_visibility(self) -> None:
        has_actions = self._actions_layout.count() > 0
        has_title = self.title_label.isVisible() and bool(self.title_label.text().strip())
        show_header = self._header_enabled and (has_title or has_actions)

        self._header_row.setVisible(show_header)
        self._separator.setVisible(show_header and self._separator_enabled)


__all__ = ["PanelCard"]
