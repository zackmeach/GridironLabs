from __future__ import annotations

import os

from PySide6 import QtCore, QtWidgets

from gridironlabs.app import bootstrap
from gridironlabs.core import load_config, setup_logging
from gridironlabs.ui.widgets.navigation_bar import NavigationBar

# Ensure headless runs do not require a visible display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_main_window_navigation_changes_page(qtbot) -> None:
    config = load_config()
    logger = setup_logging(config.paths)

    window = bootstrap(config, logger)
    qtbot.addWidget(window)

    nav_bar = window.findChild(NavigationBar)
    assert nav_bar is not None

    stack = window.findChild(QtWidgets.QStackedWidget, "contentStack")
    assert stack is not None

    target_button = nav_bar.section_buttons["teams"]
    qtbot.mouseClick(target_button, QtCore.Qt.MouseButton.LeftButton)
    qtbot.wait(20)

    assert window.current_page == "teams"
    assert stack.currentWidget().objectName() == "teamsPage"
