import pytest
from PySide6.QtCore import Qt

from gridironlabs.ui.table.columns import ColumnSpec
from gridironlabs.ui.table.delegates import RatingColorDelegate
from gridironlabs.ui.table.models import ColumnTableModel, TableRow
from gridironlabs.ui.table.ootp_table_view import OOTPTableView


@pytest.mark.qt
def test_rating_color_delegate_installs_and_paints_without_exception(qtbot):
    columns = (
        ColumnSpec("name", "NAME", 200, Qt.AlignLeft | Qt.AlignVCenter),
        ColumnSpec("ovr", "OVR", 80, Qt.AlignRight | Qt.AlignVCenter),
    )
    model = ColumnTableModel(columns=columns, rows=[TableRow(values={"name": "P1", "ovr": 80})])

    view = OOTPTableView(row_height=24)
    qtbot.addWidget(view)
    view.set_source_model(model)
    view.setItemDelegateForColumn(1, RatingColorDelegate(view))
    view.show()
    qtbot.waitExposed(view)

    # Smoke: force a paint; pytest-qt will surface Qt event loop exceptions.
    view.viewport().update()
    qtbot.wait(50)

