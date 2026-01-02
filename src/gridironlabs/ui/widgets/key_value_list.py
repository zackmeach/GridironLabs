"""Key/value list widget (read-only form rows).

OOTP-like detail panels frequently use dense key/value tables with alternating
row stripes and occasional embedded controls (e.g., a dropdown in the value column).
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget


@dataclass(frozen=True)
class KeyValueItem:
    key: str
    value: str | None = None
    value_widget: QWidget | None = None


class KeyValueRow(QFrame):
    def __init__(
        self,
        *,
        key: str,
        value: str | None = None,
        value_widget: QWidget | None = None,
        row_index: int = 0,
        key_width: int | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("KeyValueRow")
        self.setProperty("rowIndex", int(row_index))
        self.setProperty("stripe", "odd" if (row_index % 2) else "even")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        key_label = QLabel(key)
        key_label.setObjectName("KeyValueKey")
        key_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        key_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        if key_width is not None:
            key_label.setFixedWidth(int(key_width))
        layout.addWidget(key_label)

        if value_widget is not None:
            value_widget.setParent(self)
            value_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            layout.addWidget(value_widget, 1, Qt.AlignVCenter)
        else:
            value_label = QLabel(value or "")
            value_label.setObjectName("KeyValueValue")
            value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            value_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            layout.addWidget(value_label, 1, Qt.AlignVCenter)


class KeyValueList(QFrame):
    """Vertical stack of KeyValueRow items."""

    def __init__(self, *, key_width: int = 190) -> None:
        super().__init__()
        self.setObjectName("KeyValueList")
        self._key_width = int(key_width)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._rows: list[KeyValueRow] = []

    def clear(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            if w := item.widget():
                w.setParent(None)
        self._rows.clear()

    def add_item(self, item: KeyValueItem) -> None:
        self.add_row(key=item.key, value=item.value, value_widget=item.value_widget)

    def add_row(self, *, key: str, value: str | None = None, value_widget: QWidget | None = None) -> None:
        row = KeyValueRow(
            key=key,
            value=value,
            value_widget=value_widget,
            row_index=len(self._rows),
            key_width=self._key_width,
        )
        self._rows.append(row)
        self._layout.addWidget(row)

    @property
    def row_count(self) -> int:
        return len(self._rows)


__all__ = ["KeyValueItem", "KeyValueList", "KeyValueRow"]

