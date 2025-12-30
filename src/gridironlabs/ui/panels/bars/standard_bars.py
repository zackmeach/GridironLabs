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
        # Prevent invisible-content bugs: adding content implies visibility.
        self.setVisible(True)

    def add_right(self, widget: QWidget) -> None:
        self.right_slot.addWidget(widget)
        # Prevent invisible-content bugs: adding content implies visibility.
        self.setVisible(True)

    def _slot_widget_count(self, slot: QHBoxLayout) -> int:
        count = 0
        for i in range(slot.count()):
            item = slot.itemAt(i)
            if item is None:
                continue
            if item.widget() is not None:
                count += 1
        return count

    def update_visibility(self) -> None:
        """Default rule: hide if both slots are empty."""
        has_any = (self._slot_widget_count(self.left_slot) + self._slot_widget_count(self.right_slot)) > 0
        self.setVisible(has_any)

    def clear(self) -> None:
        """Remove all widgets from left/right slots."""
        for slot in (self.left_slot, self.right_slot):
            while slot.count():
                item = slot.takeAt(0)
                if item is None:
                    continue
                if w := item.widget():
                    w.setParent(None)
        self.update_visibility()


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
        self.update_visibility()

    def add_right(self, widget: QWidget) -> None:
        super().add_right(widget)
        self.update_visibility()

    def update_visibility(self) -> None:
        # Primary header is visible if:
        # - title text exists, OR
        # - any non-title widgets exist in left slot, OR
        # - any widgets exist in right slot.
        #
        # This keeps the bar visible if callers add left/right content and later clear the title.
        has_title = bool(self.title_label.text().strip())
        left_count = self._slot_widget_count(self.left_slot)
        right_count = self._slot_widget_count(self.right_slot)
        has_left_extras = left_count > 1  # left slot always contains the title label
        has_right_content = right_count > 0
        self.setVisible(has_title or has_left_extras or has_right_content)

    def clear(self) -> None:
        # Preserve the title label; clear only dynamic action widgets.
        while self.right_slot.count():
            item = self.right_slot.takeAt(0)
            if item is None:
                continue
            if w := item.widget():
                w.setParent(None)
        self.update_visibility()


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


class SectionBar(PanelBar):
    """In-body section divider (e.g. Lineup, Rotation)."""

    def __init__(self, title: str = "") -> None:
        super().__init__(role="section")
        self.setObjectName("SectionBar")
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("SectionTitle")
        self.left_slot.addWidget(self.title_label)
        
    def set_title(self, text: str) -> None:
        self.title_label.setText(text)
        self.update_visibility()

    def clear(self) -> None:
        # Preserve the title label; section headers should not self-delete.
        self.update_visibility()

    def update_visibility(self) -> None:
        # Section bars are visible if:
        # - title text exists, OR
        # - any non-title widgets exist in left slot, OR
        # - any widgets exist in right slot.
        #
        # This prevents hiding a populated section bar when the title changes dynamically.
        has_title = bool(self.title_label.text().strip())
        left_count = self._slot_widget_count(self.left_slot)
        right_count = self._slot_widget_count(self.right_slot)
        has_left_extras = left_count > 1  # left slot always contains the title label
        has_right_content = right_count > 0
        self.setVisible(has_title or has_left_extras or has_right_content)


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
        self.update_visibility()

    def clear(self) -> None:
        # Preserve the meta label.
        self.set_meta("")

    def update_visibility(self) -> None:
        # Footer bar is visible if:
        # - meta text exists, OR
        # - any widgets exist in the left slot, OR
        # - any non-meta widgets exist in the right slot.
        #
        # This keeps the bar visible for footer actions even if meta is empty.
        has_meta = bool(self.meta_label.text().strip())
        left_count = self._slot_widget_count(self.left_slot)
        right_count = self._slot_widget_count(self.right_slot)
        has_left_content = left_count > 0
        has_right_extras = right_count > 1  # right slot always contains the meta label
        self.setVisible(has_meta or has_left_content or has_right_extras)
