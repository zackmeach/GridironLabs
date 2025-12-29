"""Legacy panel chrome (v1).

This module contains the current/legacy panel shells (`PanelCard`, `Card`) used
throughout the UI. The new OOTP-style panel system will live under
`gridironlabs.ui.panels` (starting with `PanelChrome`).

Keeping the legacy chrome in its own module makes it easier to replace without
mixing old/new concepts in `base_components.py`.
"""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gridironlabs.ui.style.tokens import SPACING


class TitleLabel(QLabel):
    """Unified title label with configurable style hook."""

    def __init__(
        self,
        text: str,
        *,
        alignment: Qt.Alignment = Qt.AlignLeft | Qt.AlignTop,
        object_name: str = "CardTitlePrimary",
    ) -> None:
        super().__init__(text)
        self.setObjectName(object_name)
        self.setWordWrap(True)
        self.setAlignment(alignment)


class PanelCard(QFrame):
    """Reusable panel card shell with header + body.

    NOTE: This is legacy chrome. New work should target `PanelChrome`.

    The header stack (title, link, separator) is structurally isolated from the
    body layout. This ensures consistent positioning and prevents layout drift
    regardless of what content is placed in the body or if the body is empty.
    """

    def __init__(
        self,
        title: str | None = None,
        *,
        link_text: str | None = None,
        on_link_click: Callable[[], None] | None = None,
        show_header: bool = True,
        show_separator: bool = True,
        margins: tuple[int, int, int, int] = SPACING.panel_padding,
        spacing: int = SPACING.panel_spacing,
        title_alignment: Qt.Alignment = Qt.AlignLeft | Qt.AlignTop,
        title_object_name: str = "CardTitlePrimary",
        role: str = "panel",
    ) -> None:
        super().__init__()

        self.setObjectName("PanelCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setProperty("card-role", role)

        self._header_enabled = bool(show_header)
        self._separator_enabled = bool(show_separator)

        root = QVBoxLayout(self)
        root.setContentsMargins(*margins)
        root.setSpacing(spacing)

        self._header_stack = QWidget(self)
        self._header_stack.setObjectName("PanelCardHeaderStack")
        # Force the header stack to fixed vertical size so it doesn't drift.
        self._header_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        header_stack_layout = QVBoxLayout(self._header_stack)
        header_stack_layout.setContentsMargins(0, 0, 0, 0)
        # Use the card's top margin as the spacing between title and separator
        # so they look symmetrically placed.
        header_stack_layout.setSpacing(margins[1])

        self._header_row = QWidget(self._header_stack)
        self._header_row.setObjectName("PanelCardHeader")
        # Prevent the header row from absorbing extra vertical space (which would
        # push the separator down when the body is empty).
        self._header_row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_layout = QHBoxLayout(self._header_row)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        self.title_label = TitleLabel(
            "", alignment=title_alignment, object_name=title_object_name
        )
        # Keep the title pinned to the top-left regardless of header height.
        header_layout.addWidget(self.title_label, 1, title_alignment)

        self.link_button = QPushButton()
        self.link_button.setObjectName("PanelCardLink")
        self.link_button.setCursor(Qt.PointingHandCursor)
        # Pin link to top right
        header_layout.addWidget(self.link_button, 0, Qt.AlignRight | Qt.AlignVCenter)

        header_stack_layout.addWidget(self._header_row)

        self._separator = QFrame(self._header_stack)
        self._separator.setObjectName("PanelCardSeparator")
        self._separator.setFrameShape(QFrame.HLine)
        self._separator.setFrameShadow(QFrame.Plain)
        self._separator.setLineWidth(1)
        header_stack_layout.addWidget(self._separator)

        root.addWidget(self._header_stack, 0, Qt.AlignTop)

        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(spacing)
        # Ensure the body region absorbs remaining height so the header stack
        # stays tightly sized to the title + separator.
        root.addLayout(self.body_layout, 1)

        self.set_title(title)
        self.set_link(link_text, on_link_click)
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

    def set_link(
        self, text: str | None, on_click: Callable[[], None] | None = None
    ) -> None:
        """Set the top-right link text and click handler."""
        if not text:
            self.link_button.setVisible(False)
        else:
            self.link_button.setText(text)
            self.link_button.setVisible(True)
            try:
                self.link_button.clicked.disconnect()
            except (RuntimeError, TypeError):
                pass
            if on_click:
                self.link_button.clicked.connect(on_click)
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
        has_link = not self.link_button.isHidden()
        # `isVisible()` returns False until ancestors are shown, which would hide
        # the header permanently during construction. Use `isHidden()` instead.
        has_title = (not self.title_label.isHidden()) and bool(
            self.title_label.text().strip()
        )
        show_header = self._header_enabled and (has_title or has_link)

        self._header_stack.setVisible(show_header)
        self._separator.setVisible(show_header and self._separator_enabled)


class Card(PanelCard):
    """Base card shell with optional title and enforced chrome."""

    def __init__(
        self,
        title: str | None = None,
        *,
        role: str = "primary",
        margins: tuple[int, int, int, int] = (12, 12, 12, 12),
        spacing: int = 10,
        show_separator: bool = True,
        title_alignment: Qt.Alignment = Qt.AlignLeft | Qt.AlignTop,
        title_object_name: str = "CardTitlePrimary",
    ) -> None:
        super().__init__(
            title=title,
            link_text=None,
            on_link_click=None,
            show_header=bool(title),
            show_separator=show_separator,
            margins=margins,
            spacing=spacing,
            title_alignment=title_alignment,
            title_object_name=title_object_name,
            role=role,
        )
        self.setObjectName("Card")
        # Ensure the separator matches Card-specific styling selectors
        self._separator.setObjectName("CardSeparator")


__all__ = ["PanelCard", "Card", "TitleLabel"]


