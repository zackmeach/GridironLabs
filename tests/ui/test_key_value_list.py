import pytest
from PySide6.QtWidgets import QLabel

from gridironlabs.ui.widgets.key_value_list import KeyValueItem, KeyValueList


@pytest.mark.qt
def test_key_value_list_renders_stripes_and_supports_value_widget(qtbot):
    kv = KeyValueList(key_width=180)
    qtbot.addWidget(kv)

    kv.add_item(KeyValueItem(key="Age", value="23 years"))
    kv.add_item(KeyValueItem(key="Team", value="PIT"))
    kv.add_row(key="Projected role", value_widget=QLabel("MLB (MLB)"))

    assert kv.row_count == 3
    assert kv.objectName() == "KeyValueList"

    from gridironlabs.ui.widgets.key_value_list import KeyValueRow  # local import

    kv_rows = kv.findChildren(KeyValueRow)
    assert len(kv_rows) == 3
    assert kv_rows[0].property("stripe") == "even"
    assert kv_rows[1].property("stripe") == "odd"
