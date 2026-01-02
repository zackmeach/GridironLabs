import pytest

from gridironlabs.ui.pages.table_demo_page import TableDemoPage


@pytest.mark.qt
def test_table_demo_page_instantiates_and_contains_ootp_table_view(qtbot):
    page = TableDemoPage()
    qtbot.addWidget(page)
    page.resize(1100, 800)
    page.show()
    qtbot.waitExposed(page)

    from gridironlabs.ui.table.ootp_table_view import OOTPTableView  # local import

    view = page.findChild(OOTPTableView, "OOTPTableView")
    assert view is not None
    assert view.model() is not None
    # Proxy wraps the model, but row count should be large.
    assert view.model().rowCount() >= 1000
