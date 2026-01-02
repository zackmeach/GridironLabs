"""Compact filter/toolbar row for secondary header bars.

Goal: prevent pages from inventing bespoke spacing/height rules for OOTP-style toolbars.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QSizePolicy, QWidget


@dataclass(frozen=True)
class FilterControl:
    widget: QWidget
    tooltip: str | None = None


class CompactFilterBar(QFrame):
    """Single-row toolbar with left controls and optional right summary/actions.

    Overflow strategy:
    - Prefer constrained control widths.
    - This widget never wraps.
    - Optional last-resort horizontal scrolling inside the bar can be enabled.
    """

    def __init__(
        self,
        *,
        height: int = 26,
        spacing: int = 8,
        allow_horizontal_scroll: bool = False,
    ) -> None:
        super().__init__()
        self.setObjectName("CompactFilterBar")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(int(height))

        self._root = QHBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(int(spacing))

        self._content = QWidget(self)
        self._content.setObjectName("CompactFilterBarContent")
        self._content_layout = QHBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(int(spacing))

        self._left = QHBoxLayout()
        self._left.setContentsMargins(0, 0, 0, 0)
        self._left.setSpacing(int(spacing))
        self._left.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self._right = QHBoxLayout()
        self._right.setContentsMargins(0, 0, 0, 0)
        self._right.setSpacing(int(spacing))
        self._right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._content_layout.addLayout(self._left)
        self._content_layout.addStretch(1)
        self._content_layout.addLayout(self._right)

        if allow_horizontal_scroll:
            scroll = QScrollArea(self)
            scroll.setObjectName("CompactFilterBarScroll")
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setWidgetResizable(True)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll.setWidget(self._content)
            self._root.addWidget(scroll)
        else:
            self._root.addWidget(self._content)

        self._summary_label: QLabel | None = None

    def add_left(self, widget: QWidget, *, tooltip: str | None = None) -> None:
        widget.setParent(self._content)
        if tooltip:
            widget.setToolTip(tooltip)
        self._left.addWidget(widget)

    def add_right(self, widget: QWidget, *, tooltip: str | None = None) -> None:
        widget.setParent(self._content)
        if tooltip:
            widget.setToolTip(tooltip)
        self._right.addWidget(widget)

    def set_summary_text(self, text: str | None) -> None:
        if text is None or not str(text).strip():
            if self._summary_label is not None:
                self._summary_label.setParent(None)
                self._summary_label = None
            return
        if self._summary_label is None:
            lbl = QLabel()
            lbl.setObjectName("CompactFilterSummary")
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self._summary_label = lbl
            self._right.insertWidget(0, lbl)
        self._summary_label.setText(str(text))


__all__ = ["CompactFilterBar", "FilterControl"]

