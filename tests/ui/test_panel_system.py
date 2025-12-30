import logging

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from gridironlabs.core.config import AppPaths, load_config
from gridironlabs.ui.main_window import GridironLabsMainWindow
from gridironlabs.ui.panels import PanelChrome
from gridironlabs.ui.panels.bars.standard_bars import PrimaryHeaderBar, SecondaryHeaderBar
from gridironlabs.ui.widgets.standings import StandingsRow
from gridironlabs.ui.panels.bars.standard_bars import FooterBar, SectionBar


@pytest.mark.qt
def test_panelbar_add_autoshows_and_clear_autohides(qtbot):
    bar = SecondaryHeaderBar()
    qtbot.addWidget(bar)
    bar.hide()
    assert bar.isHidden()

    bar.add_left(QLabel("FILTER"))
    assert not bar.isHidden()

    bar.clear()
    assert bar.isHidden()


@pytest.mark.qt
def test_primary_header_clear_preserves_title(qtbot):
    bar = PrimaryHeaderBar("TITLE")
    qtbot.addWidget(bar)
    bar.show()
    assert not bar.isHidden()

    bar.add_right(QLabel("ACTION"))
    bar.clear()

    assert bar.title_label.text() == "TITLE"
    assert bar.right_slot.count() == 0
    assert not bar.isHidden()

@pytest.mark.qt
def test_primary_header_stays_visible_if_left_content_exists_even_when_title_empty(qtbot):
    bar = PrimaryHeaderBar("TITLE")
    qtbot.addWidget(bar)
    bar.show()

    bar.add_left(QLabel("EXTRA"))
    bar.set_title("")
    assert not bar.isHidden()


@pytest.mark.qt
def test_footer_stays_visible_if_left_content_exists_even_when_meta_empty(qtbot):
    bar = FooterBar()
    qtbot.addWidget(bar)
    bar.show()

    bar.add_left(QLabel("LEFT"))
    bar.set_meta("")
    assert not bar.isHidden()


@pytest.mark.qt
def test_sectionbar_stays_visible_if_right_content_exists_even_when_title_empty(qtbot):
    bar = SectionBar("TITLE")
    qtbot.addWidget(bar)
    bar.show()

    bar.add_right(QLabel("RIGHT"))
    bar.set_title("")
    assert not bar.isHidden()


@pytest.mark.qt
def test_panelchrome_table_variant_defaults_to_zero_body_padding(qtbot):
    panel = PanelChrome(title="TABLE", panel_variant="table")
    qtbot.addWidget(panel)
    margins = panel._body_layout.contentsMargins()  # noqa: SLF001 - test invariant
    assert (margins.left(), margins.top(), margins.right(), margins.bottom()) == (0, 0, 0, 0)


@pytest.mark.qt
def test_standings_row_click_navigates_to_team_summary(qtbot, monkeypatch, tmp_path):
    root = tmp_path / "app"
    root.mkdir()
    monkeypatch.setenv("GRIDIRONLABS_ROOT", str(root))

    paths = AppPaths.from_env()
    config = load_config(paths, env_file=None)
    logger = logging.getLogger("gridironlabs.ui.test")

    window = GridironLabsMainWindow(config=config, paths=paths, logger=logger)
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)

    # Click the first standings row on the home page.
    home_page = window.pages["home"]
    standings_rows = home_page.findChildren(StandingsRow)
    assert standings_rows, "Expected at least one standings row"

    qtbot.mouseClick(standings_rows[0], Qt.LeftButton)
    assert window.content_stack.currentWidget().objectName() == "page-team-summary"


