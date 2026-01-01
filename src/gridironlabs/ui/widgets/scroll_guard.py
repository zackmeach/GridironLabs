"""Scroll-area utilities for enforcing OOTP-style 'locked surface' behavior.

The UI contract for many panels is: if content visually fits, the surface should feel
perfectly locked (no accidental 1px wheel scroll). In practice, tiny 1px layout
rounding/border mismatches can produce a scrollbar range of 1, which feels like a bug.

`MicroScrollGuard` suppresses that by treating overflow <= threshold as 'fits', while
restoring normal scrolling when overflow becomes meaningful.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QTimer, Qt
from PySide6.QtWidgets import QAbstractScrollArea


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
            max_scroll = int(self._vbar.maximum())
            if max_scroll <= self._threshold_px:
                # Treat as 'fits': lock the surface at the top.
                if self._vbar.value() != 0:
                    self._vbar.setValue(0)
                self._vbar.setEnabled(False)
                if self._area.verticalScrollBarPolicy() != Qt.ScrollBarAlwaysOff:
                    self._area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            else:
                # Meaningful overflow: restore normal behavior.
                self._vbar.setEnabled(True)
                if self._area.verticalScrollBarPolicy() != self._normal_policy:
                    self._area.setVerticalScrollBarPolicy(self._normal_policy)
        finally:
            self._in_apply = False


__all__ = ["MicroScrollGuard"]


