import pytest
from PySide6.QtCore import QSettings, Qt

from gridironlabs.ui.table.columns import ColumnSpec
from gridironlabs.ui.table.models import ColumnTableModel, TableRow
from gridironlabs.ui.table.ootp_table_view import OOTPTableView, TablePersistenceKey


@pytest.mark.qt
def test_ootp_table_view_persists_column_widths_and_sort(tmp_path, qtbot):
    ini_path = tmp_path / "ui.ini"
    settings = QSettings(str(ini_path), QSettings.IniFormat)

    columns = (
        ColumnSpec("name", "NAME", 200, Qt.AlignLeft | Qt.AlignVCenter),
        ColumnSpec("age", "AGE", 60, Qt.AlignRight | Qt.AlignVCenter),
    )
    rows = [TableRow(values={"name": f"Player {i}", "age": 20 + (i % 10)}) for i in range(50)]
    model = ColumnTableModel(columns=columns, rows=rows)

    view1 = OOTPTableView(row_height=24)
    qtbot.addWidget(view1)
    view1.enable_persistence(settings=settings, key=TablePersistenceKey(page_id="test", table_id="t1"))
    view1.set_source_model(model)
    view1.resize(900, 500)
    view1.show()
    qtbot.waitExposed(view1)

    view1.setColumnWidth(0, 333)
    view1.sortByColumn(1, Qt.DescendingOrder)
    qtbot.wait(50)
    assert view1.columnWidth(0) == 333
    # Ensure persistence write occurred.
    stored = settings.value("ui/pages/test/tables/t1/v1/columns/widths")
    assert stored
    assert str(stored).split(",")[0] == "333"

    # New instance should restore persisted state.
    view2 = OOTPTableView(row_height=24)
    qtbot.addWidget(view2)
    view2.enable_persistence(settings=settings, key=TablePersistenceKey(page_id="test", table_id="t1"))
    view2.set_source_model(model)
    view2.resize(900, 500)
    view2.show()
    qtbot.waitExposed(view2)

    qtbot.waitUntil(lambda: view2.restored_once, timeout=1500)
    qtbot.waitUntil(lambda: view2.columnWidth(0) == 333, timeout=1500)
    assert view2.columnWidth(0) == 333
    assert view2.horizontalHeader().sortIndicatorSection() == 1
    assert view2.horizontalHeader().sortIndicatorOrder() == Qt.DescendingOrder

