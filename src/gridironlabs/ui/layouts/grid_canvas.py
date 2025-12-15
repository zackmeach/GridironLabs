"""Page content grid canvas.



This is a thin wrapper around a 24-column QGridLayout that provides a stable API

for placing panel widgets by grid coordinates.



Grid units are discrete (col/row integers); the debug overlay is optional and is

driven by a shared GridOverlayConfig.

"""



from __future__ import annotations



from dataclasses import dataclass



from PySide6.QtCore import Qt

from PySide6.QtWidgets import QFrame, QGridLayout, QSizePolicy, QWidget



from gridironlabs.ui.overlays.grid_overlay import GridOverlay, GridOverlayConfig

from gridironlabs.ui.style.tokens import GRID, SPACING





@dataclass(frozen=True)

class PanelDescriptor:

    """Declarative panel placement."""



    widget: QWidget

    col: int

    row: int

    col_span: int = 1

    row_span: int = 1

    alignment: Qt.Alignment = Qt.Alignment()





class GridCanvas(QFrame):

    """A reusable grid-based canvas for placing panel cards."""



    def __init__(

        self,

        parent: QWidget | None = None,

        *,

        cols: int = GRID.cols,

        rows: int | None = None,

        gap: int = SPACING.grid_gap,

        overlay_config: GridOverlayConfig | None = None,

    ) -> None:

        super().__init__(parent)

        self.setObjectName("GridCanvas")



        self._cols = max(1, int(cols))

        self._rows = int(rows) if rows is not None else None



        self._layout = QGridLayout(self)

        self._layout.setContentsMargins(0, 0, 0, 0)

        self._layout.setHorizontalSpacing(int(gap))

        self._layout.setVerticalSpacing(int(gap))



        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)



        self.overlay_config = overlay_config or GridOverlayConfig()

        self._overlay = GridOverlay(self, cols=self._cols, config=self.overlay_config)

        self._overlay.raise_()



        self._max_row_used = 0

        self._apply_column_stretches()

        self._apply_row_stretches()



    @property

    def cols(self) -> int:

        return self._cols



    @property

    def rows(self) -> int | None:

        return self._rows



    def set_grid_config(self, *, cols: int | None = None, rows: int | None = None, gap: int | None = None) -> None:

        """Update grid sizing parameters.



        The grid is discrete; changing the number of columns does not reflow existing

        placements. Prefer keeping `cols` stable (24) and only changing `rows`/`gap`.

        """



        if cols is not None:

            self._cols = max(1, int(cols))

            self._apply_column_stretches()

            self._overlay.set_cols(self._cols)



        if rows is not None:

            self._rows = max(1, int(rows))

            self._apply_row_stretches()



        if gap is not None:

            value = max(0, int(gap))

            self._layout.setHorizontalSpacing(value)

            self._layout.setVerticalSpacing(value)



        self.update()



    def current_row_pitch_px(self) -> int | None:
        """Return the current per-row pitch in pixels.

        This is the distance from the top of row N to the top of row N+1. It is
        derived from the live canvas size, the configured row count (if any), and
        the current QGridLayout vertical spacing.
        """

        if self._rows is None:
            return None

        rect = self.contentsRect()
        height = rect.height()
        if height <= 0:
            return None

        gap = self._layout.verticalSpacing()
        return max(1, round((height + gap) / self._rows))

    def current_column_pitch_px(self) -> int | None:
        """Return the current per-column pitch in pixels.

        This is the distance from the left edge of column N to the left edge of
        column N+1. It is derived from the live canvas size, the column count,
        and the current QGridLayout horizontal spacing.
        """

        rect = self.contentsRect()
        width = rect.width()
        if width <= 0:
            return None

        gap = self._layout.horizontalSpacing()
        return max(1, round((width + gap) / self._cols))

    def add_panel(

        self,

        widget: QWidget,

        *,

        col: int,

        row: int,

        col_span: int = 1,

        row_span: int = 1,

        alignment: Qt.Alignment = Qt.Alignment(),

    ) -> None:

        """Place a widget at a grid coordinate."""



        col = max(0, int(col))

        row = max(0, int(row))

        col_span = max(1, int(col_span))

        row_span = max(1, int(row_span))



        if col + col_span > self._cols:

            col_span = max(1, self._cols - col)



        widget.setParent(self)

        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._layout.addWidget(widget, row, col, row_span, col_span, alignment)
        self._overlay.raise_()



        self._max_row_used = max(self._max_row_used, row + row_span)

        self._apply_row_stretches()



    def add_panels(self, descriptors: list[PanelDescriptor]) -> None:

        for desc in descriptors:

            self.add_panel(

                desc.widget,

                col=desc.col,

                row=desc.row,

                col_span=desc.col_span,

                row_span=desc.row_span,

                alignment=desc.alignment,

            )



    def clear_panels(self) -> None:

        """Remove all placed panels."""



        while self._layout.count():

            item = self._layout.takeAt(0)

            if widget := item.widget():

                widget.setParent(None)

        self._max_row_used = 0

        self._apply_row_stretches()



    def resizeEvent(self, event) -> None:  # pragma: no cover - UI resize

        super().resizeEvent(event)

        self._overlay.setGeometry(self.rect())

        self._overlay.raise_()



    def _apply_column_stretches(self) -> None:

        for col in range(self._cols):

            self._layout.setColumnStretch(col, 1)



    def _apply_row_stretches(self) -> None:

        target_rows = self._rows if self._rows is not None else max(1, self._max_row_used)

        for row in range(target_rows):

            self._layout.setRowStretch(row, 1)

