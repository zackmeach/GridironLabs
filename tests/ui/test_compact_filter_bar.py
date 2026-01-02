import pytest
from PySide6.QtWidgets import QLabel

from gridironlabs.ui.widgets.compact_filter_bar import CompactFilterBar


@pytest.mark.qt
def test_compact_filter_bar_has_fixed_height_and_does_not_wrap(qtbot):
    bar = CompactFilterBar(height=26, spacing=6, allow_horizontal_scroll=False)
    qtbot.addWidget(bar)
    bar.show()

    for i in range(12):
        bar.add_left(QLabel(f"CTRL{i}"))

    assert bar.height() == 26
    assert bar.sizeHint().height() <= 26
