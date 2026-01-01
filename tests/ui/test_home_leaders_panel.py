import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from gridironlabs.core.models import EntitySummary
from gridironlabs.ui.widgets.leaders import LeagueLeadersWidget


def _player(*, pid: str, name: str, pos: str, stats: dict[str, float]) -> EntitySummary:
    return EntitySummary(id=pid, name=name, entity_type="player", position=pos, stats=stats)


@pytest.mark.qt
def test_league_leaders_widget_renders_category_row_counts_and_sorts_best_to_worst(qtbot):
    players: list[EntitySummary] = []

    # PASSING (QB)
    players.extend(
        [
            _player(
                pid="qb-1",
                name="QB One",
                pos="QB",
                stats={
                    "passing_yards": 4872,
                    "passing_completions": 410,
                    "passing_attempts": 520,
                    "passing_tds": 41,
                    "interceptions": 13,
                    "qbr": 66.0,
                    "wpa_total": 1.2,
                },
            ),
            _player(
                pid="qb-2",
                name="QB Two",
                pos="QB",
                stats={
                    "passing_yards": 4103,
                    "passing_completions": 360,
                    "passing_attempts": 480,
                    "passing_tds": 38,
                    "interceptions": 6,
                    "qbr": 79.0,
                    "wpa_total": 0.8,
                },
            ),
            _player(
                pid="qb-3",
                name="QB Three",
                pos="QB",
                stats={
                    "passing_yards": 3266,
                    "passing_completions": 300,
                    "passing_attempts": 410,
                    "passing_tds": 33,
                    "interceptions": 19,
                    "qbr": 73.0,
                    "wpa_total": 0.2,
                },
            ),
        ]
    )

    # RUSHING (RB)
    for i in range(1, 4):
        players.append(
            _player(
                pid=f"rb-{i}",
                name=f"RB {i}",
                pos="RB",
                stats={
                    "rushing_yards": 1000 - i * 10,
                    "rushing_attempts": 200 + i,
                    "rushing_tds": 10 + i,
                    "fumbles": float(i),  # lower is better
                    "rush_20_plus": 3 + i,
                    "wpa_total": 0.1 * i,
                },
            )
        )

    # RECEIVING (WR)
    for i in range(1, 4):
        players.append(
            _player(
                pid=f"wr-{i}",
                name=f"WR {i}",
                pos="WR",
                stats={
                    "receiving_yards": 1200 - i * 12,
                    "receptions": 80 + i,
                    "receiving_targets": 110 + i,
                    "receiving_tds": 8 + i,
                    "receiving_yac": 350 + i,
                    "wpa_total": 0.05 * i,
                },
            )
        )

    # KICKING (K)
    for i in range(1, 4):
        players.append(
            _player(
                pid=f"k-{i}",
                name=f"K {i}",
                pos="K",
                stats={
                    "field_goals_made": 30 + i,
                    "field_goals_attempted": 35 + i,
                    "fg_made_under_29": 10 + i,
                    "fg_made_30_39": 8 + i,
                    "fg_made_40_49": 7 + i,
                    "fg_made_50_plus": 5 + i,
                    "wpa_total": 0.03 * i,
                },
            )
        )

    # DEFENSE (LB)
    for i in range(1, 16):
        players.append(
            _player(
                pid=f"lb-{i}",
                name=f"LB {i}",
                pos="LB",
                stats={
                    "tackles": 120 - i,
                    "tackles_for_loss": 12 + (i % 3),
                    "sacks": 8 + (i % 4),
                    "forced_fumbles": float(i % 2),
                    "def_interceptions": float(i % 5),
                    "passes_defended": 10 + (i % 4),
                    "wpa_total": 0.02 * i,
                },
            )
        )

    widget = LeagueLeadersWidget()
    qtbot.addWidget(widget)
    widget.resize(900, 800)
    widget.show()
    qtbot.waitExposed(widget)
    widget.set_players(players)

    from PySide6.QtWidgets import QFrame  # local import for test clarity

    sections = widget.findChildren(QFrame, "LeadersCategorySection")
    assert len(sections) == 5

    passing_section = next(s for s in sections if s.property("categoryKey") == "passing")
    defense_section = next(s for s in sections if s.property("categoryKey") == "defense")

    assert len(passing_section.findChildren(QFrame, "LeadersRow")) == 5
    assert len(defense_section.findChildren(QFrame, "LeadersRow")) == 12

    # Click PASSING INT header in the category bar: should sort ascending (best-to-worst for INT).
    int_headers = [
        w
        for w in passing_section.findChildren(QLabel, "LeadersBarStatHeader")
        if w.text() == "INT" and w.isEnabled()
    ]
    assert int_headers, "Expected INT header in PASSING section"
    qtbot.mouseClick(int_headers[0], Qt.LeftButton)

    first_row = passing_section.findChildren(QFrame, "LeadersRow")[0]
    first_name = first_row.findChild(QLabel, "LeadersCellPlayer").text()
    assert first_name == "QB Two"  # 6 INT is best among sample QBs

    # Clicking again should not toggle to worst-to-best.
    qtbot.mouseClick(int_headers[0], Qt.LeftButton)
    first_row_again = passing_section.findChildren(QFrame, "LeadersRow")[0]
    first_name_again = first_row_again.findChild(QLabel, "LeadersCellPlayer").text()
    assert first_name_again == "QB Two"


