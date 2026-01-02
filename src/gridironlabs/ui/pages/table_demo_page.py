"""Dev-only table demo page used to validate OOTPTableView behavior at scale."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from gridironlabs.ui.pages.base_page import BasePage
from gridironlabs.ui.panels import PanelChrome
from gridironlabs.ui.style.tokens import GRID
from gridironlabs.ui.table.columns import ColumnSpec
from gridironlabs.ui.table.models import ColumnTableModel, RowRole, TableRow
from gridironlabs.ui.table.ootp_table_view import OOTPTableView, TablePersistenceKey
from gridironlabs.ui.table.delegates import RatingColorDelegate


class TableDemoPage(BasePage):
    def __init__(self) -> None:
        super().__init__(cols=GRID.cols, rows=12)
        self.setObjectName("page-table-demo")

        panel = PanelChrome(title="TABLE DEMO", panel_variant="table")
        panel.set_footer_text("Dev-only: 1,000+ rows to validate QTableView + proxy sorting.")

        view = OOTPTableView(row_height=24, scroll_variant=None)
        # Enable persistence using application QSettings (organization/app set in ui/app.py).
        try:
            from PySide6.QtCore import QSettings

            view.enable_persistence(settings=QSettings(), key=TablePersistenceKey(page_id="table-demo", table_id="demo"))
        except Exception:
            pass

        columns = (
            ColumnSpec("pos", "POS", 60, Qt.AlignLeft | Qt.AlignVCenter),
            ColumnSpec("name", "NAME", 220, Qt.AlignLeft | Qt.AlignVCenter),
            ColumnSpec("age", "AGE", 60, Qt.AlignRight | Qt.AlignVCenter),
            ColumnSpec("overall", "OVR", 80, Qt.AlignRight | Qt.AlignVCenter),
            ColumnSpec("potential", "POT", 80, Qt.AlignRight | Qt.AlignVCenter),
        )

        rows: list[TableRow] = []
        rows.append(TableRow(values={"pos": "—", "name": "Players (1k demo)", "age": "", "overall": "", "potential": ""}, row_role=RowRole.GROUP))
        for i in range(1, 1101):
            rows.append(
                TableRow(
                    values={
                        "pos": "RB" if i % 4 == 0 else ("QB" if i % 5 == 0 else "WR"),
                        "name": f"Player {i}",
                        "age": 20 + (i % 15),
                        "overall": 20 + (i % 80),
                        "potential": 20 + ((i * 3) % 80),
                    },
                    row_role=RowRole.DATA,
                )
            )
        rows.append(
            TableRow(
                values={"pos": "", "name": "TOTAL", "age": "", "overall": "—", "potential": "—"},
                row_role=RowRole.SUMMARY,
            )
        )

        model = ColumnTableModel(columns=columns, rows=rows)
        view.set_source_model(model)
        # Apply initial column widths
        for idx, spec in enumerate(columns):
            view.setColumnWidth(idx, spec.width)
        # Delegate: rating-colored numbers for OVR/POT.
        view.setItemDelegateForColumn(3, RatingColorDelegate(view))
        view.setItemDelegateForColumn(4, RatingColorDelegate(view))

        panel.set_body(view)
        self.add_panel(panel, col=0, row=0, col_span=36, row_span=12)


__all__ = ["TableDemoPage"]

