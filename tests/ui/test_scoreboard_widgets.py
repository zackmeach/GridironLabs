import pytest

from gridironlabs.ui.widgets.callout_strip import CalloutStrip
from gridironlabs.ui.widgets.scoreboard import FooterButtonRow, ScoreboardLine, ScoreboardWidget


@pytest.mark.qt
def test_callout_strip_renders_and_sets_intent(qtbot):
    strip = CalloutStrip(left_text="LOSS", right_text="Sep. 28th", intent="danger")
    qtbot.addWidget(strip)
    strip.show()
    qtbot.waitExposed(strip)
    assert strip.objectName() == "CalloutStrip"
    assert strip.property("intent") == "danger"


@pytest.mark.qt
def test_scoreboard_widget_renders_two_lines(qtbot):
    board = ScoreboardWidget(innings=9)
    qtbot.addWidget(board)
    board.set_lines(
        [
            ScoreboardLine(team="Pittsburgh", runs_by_inning=[0] * 9, r=1, h=6, e=1),
            ScoreboardLine(team="Atlanta", runs_by_inning=[2, 0, 0, 0, 0, 0, 0, 2, 0], r=4, h=6, e=0),
        ]
    )
    board.show()
    qtbot.waitExposed(board)
    assert board.objectName() == "ScoreboardWidget"


@pytest.mark.qt
def test_footer_button_row_builds_buttons(qtbot):
    row = FooterButtonRow(["REPLAY", "HIGHLIGHTS", "BOX SCORE"])
    qtbot.addWidget(row)
    row.show()
    qtbot.waitExposed(row)
    from PySide6.QtWidgets import QPushButton

    buttons = row.findChildren(QPushButton, "FooterButton")
    assert [b.text() for b in buttons] == ["REPLAY", "HIGHLIGHTS", "BOX SCORE"]

