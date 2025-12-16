import logging

import pytest
from PySide6.QtCore import Qt

from gridironlabs.core.config import AppPaths, load_config
from gridironlabs.ui.main_window import GridironLabsMainWindow


@pytest.mark.qt
def test_top_nav_switches_pages(qtbot, monkeypatch, tmp_path):
    root = tmp_path / "app"
    root.mkdir()
    monkeypatch.setenv("GRIDIRONLABS_ROOT", str(root))

    paths = AppPaths.from_env()
    config = load_config(paths, env_file=None)
    logger = logging.getLogger("gridironlabs.ui.test")

    window = GridironLabsMainWindow(
        config=config,
        paths=paths,
        logger=logger,
    )
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)

    assert window.top_nav.objectName() == "TopNavigationBar"
    assert window.content_stack.objectName() == "ContentStack"

    players_button = window.top_nav.section_buttons["players"]
    qtbot.mouseClick(players_button, Qt.LeftButton)
    assert window.content_stack.currentWidget().objectName() == "page-players"


@pytest.mark.qt
def test_settings_button_opens_settings_page(qtbot, monkeypatch, tmp_path):
    root = tmp_path / "app"
    root.mkdir()
    monkeypatch.setenv("GRIDIRONLABS_ROOT", str(root))

    paths = AppPaths.from_env()
    config = load_config(paths, env_file=None)
    logger = logging.getLogger("gridironlabs.ui.test")

    window = GridironLabsMainWindow(
        config=config,
        paths=paths,
        logger=logger,
    )
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)

    qtbot.mouseClick(window.top_nav.settings_button, Qt.LeftButton)
    assert window.content_stack.currentWidget().objectName() == "page-settings"