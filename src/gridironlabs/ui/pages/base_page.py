"""Base page implementation.



A page owns a grid canvas for placing panel cards. The main window provides the

persistent navigation + context bar; pages render only the content region below.

"""



from __future__ import annotations



from PySide6.QtWidgets import QVBoxLayout, QWidget



from gridironlabs.ui.layouts.grid_canvas import GridCanvas

from gridironlabs.ui.overlays.grid_overlay import GridOverlayConfig

from gridironlabs.ui.style.tokens import GRID, SPACING





class BasePage(QWidget):

    """A page with a reusable content grid."""



    def __init__(

        self,

        parent: QWidget | None = None,

        *,

        cols: int = GRID.cols,

        rows: int | None = None,

        overlay_config: GridOverlayConfig | None = None,

    ) -> None:

        super().__init__(parent)



        layout = QVBoxLayout(self)

        layout.setContentsMargins(*SPACING.page_margins)

        layout.setSpacing(SPACING.grid_gap)



        self.grid = GridCanvas(self, cols=cols, rows=rows, overlay_config=overlay_config)

        layout.addWidget(self.grid)



    def add_panel(self, widget, *, col: int, row: int, col_span: int = 1, row_span: int = 1) -> None:

        self.grid.add_panel(widget, col=col, row=row, col_span=col_span, row_span=row_span)



    def clear_panels(self) -> None:

        self.grid.clear_panels()

