import pytest
from PySide6.QtWidgets import QLabel

from gridironlabs.ui.widgets.charts import ChartPanelBody
from gridironlabs.ui.widgets.rich_text import RichTextPanelBody


@pytest.mark.qt
def test_rich_text_panel_body_sets_html(qtbot):
    body = RichTextPanelBody(html="<b>Hello</b>")
    qtbot.addWidget(body)
    body.show()
    qtbot.waitExposed(body)
    assert "Hello" in body.browser.toPlainText()


@pytest.mark.qt
def test_chart_panel_body_hosts_widget(qtbot):
    chart = QLabel("Chart")
    body = ChartPanelBody(chart_widget=chart)
    qtbot.addWidget(body)
    body.show()
    qtbot.waitExposed(body)
    assert body.findChild(QLabel) is chart

