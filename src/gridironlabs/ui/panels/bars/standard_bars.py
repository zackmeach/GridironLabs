"""Standard panel bars implementing the OOTP-style contract."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QWidget,
)


class PanelBar(QFrame):
    """Base class for all panel bars."""

    def __init__(self, role: str = "primary") -> None:
        super().__init__()
        self.setProperty("barRole", role)
        
        # Fixed layout structure: Left slot (title/filters) + Right slot (actions/nav)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)  # controlled by QSS padding
        self._layout.setSpacing(8)

        self.left_slot = QHBoxLayout()
        self.left_slot.setContentsMargins(0, 0, 0, 0)
        self.left_slot.setSpacing(8)
        self.left_slot.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.right_slot = QHBoxLayout()
        self.right_slot.setContentsMargins(0, 0, 0, 0)
        self.right_slot.setSpacing(8)
        self.right_slot.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._layout.addLayout(self.left_slot)
        self._layout.addStretch(1)
        self._layout.addLayout(self.right_slot)

    def add_left(self, widget: QWidget) -> None:
        self.left_slot.addWidget(widget)

    def add_right(self, widget: QWidget) -> None:
        self.right_slot.addWidget(widget)

    def clear(self) -> None:
        # Helper to clear layouts if needed
        pass


class PrimaryHeaderBar(PanelBar):
    """Row 1: Title + Panel Actions."""

    def __init__(self, title: str = "") -> None:
        super().__init__(role="primary")
        self.setObjectName("PrimaryHeaderBar")
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("PanelTitle")
        self.left_slot.addWidget(self.title_label)
        
        # Placeholder for 'More' or 'Menu' action usually found on the right
        # self.menu_button = QToolButton() ...

    def set_title(self, text: str) -> None:
        self.title_label.setText(text)
        self.setVisible(bool(text) or self.right_slot.count() > 0)


class SecondaryHeaderBar(PanelBar):
    """Row 2: Filters, Search, Date Range, Paging."""

    def __init__(self) -> None:
        super().__init__(role="secondary")
        self.setObjectName("SecondaryHeaderBar")


class TertiaryHeaderBar(PanelBar):
    """Row 3: Column Semantics / Sort Bar."""

    def __init__(self) -> None:
        super().__init__(role="tertiary")
        self.setObjectName("TertiaryHeaderBar")


class FooterBar(PanelBar):
    """Footer: Context/Meta info."""

    def __init__(self) -> None:
        super().__init__(role="footer")
        self.setObjectName("FooterBar")
        
        # Footers often have text on the right
        self.meta_label = QLabel()
        self.meta_label.setObjectName("FooterMetaLabel")
        self.right_slot.addWidget(self.meta_label)

    def set_meta(self, text: str) -> None:
        self.meta_label.setText(text)
        self.setVisible(bool(text))

