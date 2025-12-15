"""Debug grid overlay for page content canvases."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from gridironlabs.ui.style.tokens import GRID


@dataclass(frozen=True)
class GridOverlayStyle:
    """Style inputs for the debug grid overlay."""

    enabled: bool = GRID.debug_enabled
    opacity: float = GRID.debug_opacity
    color_hex: str = GRID.debug_color_hex
    cell_size: int = GRID.debug_cell_size


class GridOverlayConfig(QObject):
    """Observable configuration for grid overlays.

    This is intentionally lightweight so it can be shared between multiple
    canvases/pages (e.g., Settings toggles a global debug grid for all pages).
    """

    changed = Signal()

    def __init__(self, *, style: GridOverlayStyle | None = None) -> None:
        super().__init__()
        style = style or GridOverlayStyle()
        self._enabled = bool(style.enabled)
        self._opacity = float(style.opacity)
        self._color_hex = str(style.color_hex)
        self._cell_size = int(style.cell_size)

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def opacity(self) -> float:
        return self._opacity

    @property
    def color_hex(self) -> str:
        return self._color_hex

    @property
    def cell_size(self) -> int:
        return self._cell_size

    def set_enabled(self, enabled: bool) -> None:
        enabled = bool(enabled)
        if enabled == self._enabled:
            return
        self._enabled = enabled
        self.changed.emit()

    def set_opacity(self, opacity: float) -> None:
        try:
            value = float(opacity)
        except (TypeError, ValueError):
            return
        value = max(0.0, min(1.0, value))
        if abs(value - self._opacity) < 1e-6:
            return
        self._opacity = value
        self.changed.emit()

    def set_color_hex(self, color_hex: str) -> None:
        value = _normalize_hex(color_hex)
        if value == self._color_hex:
            return
        self._color_hex = value
        self.changed.emit()

    def set_cell_size(self, cell_size: int) -> None:
        try:
            value = int(cell_size)
        except (TypeError, ValueError):
            return
        value = max(6, min(200, value))
        if value == self._cell_size:
            return
        self._cell_size = value
        self.changed.emit()


class GridOverlay(QWidget):
    """Paints a configurable debug grid over its parent canvas."""

    def __init__(self, parent: QWidget, *, cols: int, config: GridOverlayConfig) -> None:
        super().__init__(parent)
        self.setObjectName("GridOverlay")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._cols = max(1, int(cols))
        self._config = config
        self._config.changed.connect(self._on_config_changed)
        self._on_config_changed()

    def set_cols(self, cols: int) -> None:
        value = max(1, int(cols))
        if value == self._cols:
            return
        self._cols = value
        self.update()

    def _on_config_changed(self) -> None:
        self.setVisible(self._config.enabled)
        self.update()

    def paintEvent(self, event) -> None:  # pragma: no cover - UI paint
        if not self._config.enabled:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        color = QColor(self._config.color_hex)
        color.setAlphaF(max(0.0, min(1.0, self._config.opacity)))
        pen = QPen(color)
        pen.setWidth(1)
        painter.setPen(pen)

        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return

        # 24-col vertical grid.
        for col in range(1, self._cols):
            x = round((col / self._cols) * w)
            painter.drawLine(x, 0, x, h)

        # Horizontal pixel grid using the cell size.
        step = max(6, int(self._config.cell_size))
        y = step
        while y < h:
            painter.drawLine(0, y, w, y)
            y += step

        painter.end()


def _normalize_hex(text: str) -> str:
    value = str(text).strip().lstrip("#")
    if len(value) not in (3, 6) or any(ch not in "0123456789abcdefABCDEF" for ch in value):
        return GRID.debug_color_hex
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    return f"#{value.lower()}"
