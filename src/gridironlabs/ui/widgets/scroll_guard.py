"""Scroll-area utilities for enforcing OOTP-style 'locked surface' behavior.

The UI contract for many panels is: if content visually fits, the surface should feel
perfectly locked (no accidental 1px wheel scroll). In practice, tiny 1px layout
rounding/border mismatches can produce a scrollbar range of 1, which feels like a bug.

`MicroScrollGuard` suppresses that by treating overflow <= threshold as 'fits', while
restoring normal scrolling when overflow becomes meaningful.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import QEvent, QObject, QTimer, Qt
from PySide6.QtWidgets import QAbstractScrollArea, QFrame, QScrollArea, QWidget

from gridironlabs.ui.style.tokens import GRID


class MicroScrollGuard(QObject):
    """Disable vertical scrolling when the overflow range is tiny (<= threshold_px)."""

    def __init__(
        self,
        area: QAbstractScrollArea,
        *,
        threshold_px: int = 1,
        normal_policy: Qt.ScrollBarPolicy = Qt.ScrollBarAsNeeded,
    ) -> None:
        super().__init__(area)
        self._area = area
        self._threshold_px = int(threshold_px)
        self._normal_policy = normal_policy

        self._in_apply = False
        self._refresh_scheduled = False

        self._vbar = self._area.verticalScrollBar()
        self._vbar.rangeChanged.connect(self._on_range_changed)

        # Capture viewport resizes and show/polish events; scrollbar range changes
        # are not always emitted in every style/layout edge case.
        self._area.installEventFilter(self)
        self._area.viewport().installEventFilter(self)

        # Run after initial layout.
        self.refresh()

    def _debug_log(self) -> None:
        if not GRID.debug_enabled:
            return
        logger = logging.getLogger("gridironlabs.ui.scroll_guard")
        try:
            viewport_h = int(self._area.viewport().height())
            max_scroll = int(self._vbar.maximum())
            value = int(self._vbar.value())
        except RuntimeError:
            return

        # best-effort; sizeHint can throw during teardown
        content_hint = None
        try:
            content = self._area.widget()
            if content is not None:
                content_hint = int(content.sizeHint().height())
        except RuntimeError:
            content_hint = None

        logger.debug(
            "MicroScrollGuard metrics",
            extra={
                "viewport_h": viewport_h,
                "content_hint_h": content_hint,
                "max_scroll": max_scroll,
                "value": value,
                "threshold_px": int(self._threshold_px),
            },
        )

    def refresh(self) -> None:
        """Schedule a coalesced apply pass after the current event loop turn."""
        if self._refresh_scheduled:
            return
        self._refresh_scheduled = True
        QTimer.singleShot(0, self._apply)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802 - Qt API
        et = event.type()
        if et in {
            QEvent.Resize,
            QEvent.Show,
            QEvent.LayoutRequest,
            QEvent.Polish,
            QEvent.StyleChange,
            QEvent.ParentChange,
        }:
            self.refresh()
        return super().eventFilter(obj, event)

    def _on_range_changed(self, _min: int, _max: int) -> None:
        self.refresh()

    def _apply(self) -> None:
        # Coalesced refresh marker.
        self._refresh_scheduled = False

        # Prevent signal/event cascades from re-entering while we mutate policy/value.
        if self._in_apply:
            return
        self._in_apply = True
        try:
            # Widget teardown can race with our QTimer.singleShot(0, ...).
            # In that case the underlying Qt objects may already be deleted.
            try:
                max_scroll = int(self._vbar.maximum())
            except RuntimeError:
                return
            if max_scroll <= self._threshold_px:
                # Treat as 'fits': lock the surface at the top.
                try:
                    if self._vbar.value() != 0:
                        self._vbar.setValue(0)
                    self._vbar.setEnabled(False)
                    if self._area.verticalScrollBarPolicy() != Qt.ScrollBarAlwaysOff:
                        self._area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                except RuntimeError:
                    return
            else:
                # Meaningful overflow: restore normal behavior.
                try:
                    self._vbar.setEnabled(True)
                    if self._area.verticalScrollBarPolicy() != self._normal_policy:
                        self._area.setVerticalScrollBarPolicy(self._normal_policy)
                except RuntimeError:
                    return
            self._debug_log()
        finally:
            self._in_apply = False


def make_locked_scroll(
    widget: QWidget,
    *,
    threshold_px: int = 1,
    normal_policy: Qt.ScrollBarPolicy = Qt.ScrollBarAsNeeded,
) -> QScrollArea:
    """Create an OOTP-style 'locked surface' scroll area for small/medium lists.

    - Scrollbars are visually hidden per-surface via `scrollVariant="hidden"`.
    - Scrolling remains enabled (AsNeeded).
    - MicroScrollGuard suppresses accidental 1px overflow.
    """

    scroll = QScrollArea()
    scroll.setProperty("scrollVariant", "hidden")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setVerticalScrollBarPolicy(normal_policy)
    scroll.setFocusPolicy(Qt.StrongFocus)
    scroll.setWidget(widget)

    MicroScrollGuard(scroll, threshold_px=threshold_px, normal_policy=normal_policy)
    return scroll


__all__ = ["MicroScrollGuard", "make_locked_scroll"]


