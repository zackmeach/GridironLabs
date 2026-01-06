from datetime import datetime, timedelta

import pytest
from PySide6.QtWidgets import QFrame

from gridironlabs.core.models import GameSummary
from gridironlabs.ui.panels.bars.standard_bars import SectionBar
from gridironlabs.ui.widgets.schedule import LeagueScheduleWidget


@pytest.mark.qt
def test_schedule_groups_by_week_and_day_and_navigates(qtbot):
    widget = LeagueScheduleWidget()
    qtbot.addWidget(widget)
    widget.resize(960, 640)
    widget.show()
    qtbot.waitExposed(widget)

    base = datetime(2024, 9, 7, 19, 15)
    games = [
        GameSummary(
            id="g1",
            season=2024,
            week=1,
            home_team="GB",
            away_team="CHI",
            location="Lambeau Field",
            start_time=base,
            status="scheduled",
        ),
        GameSummary(
            id="g2",
            season=2024,
            week=1,
            home_team="KC",
            away_team="DEN",
            location="GEHA Field",
            start_time=base + timedelta(days=1, hours=2),
            status="final",
            home_score=31,
            away_score=21,
        ),
        GameSummary(
            id="g3",
            season=2024,
            week=2,
            home_team="NE",
            away_team="MIA",
            location="Gillette Stadium",
            start_time=base + timedelta(days=7),
            status="scheduled",
        ),
    ]

    widget.set_games(games)

    assert widget.current_group_label() == "Week 1"
    day_bars_week1 = widget.findChildren(SectionBar)
    assert [bar.title_label.text() for bar in day_bars_week1] == ["Sat, Sep 7", "Sun, Sep 8"]
    rows_week1 = widget.findChildren(QFrame, "ScheduleRow")
    assert len(rows_week1) == 2

    widget.next_group()

    assert widget.current_group_label() == "Week 2"
    day_bars_week2 = widget.findChildren(SectionBar)
    assert [bar.title_label.text() for bar in day_bars_week2] == ["Sat, Sep 14"]
    rows_week2 = widget.findChildren(QFrame, "ScheduleRow")
    assert len(rows_week2) == 1
