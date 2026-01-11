import logging

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from gridironlabs.core.config import AppPaths, load_config
from gridironlabs.ui.main_window import GridironLabsMainWindow
from gridironlabs.ui.panels import PanelChrome
from gridironlabs.ui.panels.bars.standard_bars import PrimaryHeaderBar, SecondaryHeaderBar
from gridironlabs.ui.widgets.standings import StandingsRow
from gridironlabs.ui.panels.bars.standard_bars import FooterBar, SectionBar
from gridironlabs.ui.widgets.scroll_guard import MicroScrollGuard, make_locked_scroll


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
def test_primary_header_insert_left_controls_after_title(qtbot):
    bar = PrimaryHeaderBar("TITLE")
    qtbot.addWidget(bar)
    bar.show()

    extra = QLabel("EXTRA")
    bar.add_left_after_title(extra)

    # left_slot item 0 is title label; item 1 should be EXTRA
    assert bar.left_slot.count() >= 2
    item0 = bar.left_slot.itemAt(0).widget()
    item1 = bar.left_slot.itemAt(1).widget()
    assert item0 is bar.title_label
    assert item1 is extra


@pytest.mark.qt
def test_sectionbar_set_right_columns_renders_labels(qtbot):
    bar = SectionBar("Rotation")
    qtbot.addWidget(bar)
    bar.show()

    bar.set_right_columns([("REC", 60), ("ERA", 60)])
    assert not bar.isHidden()

    labels = bar.findChildren(QLabel, "SectionColumnLabel")
    assert [lbl.text() for lbl in labels] == ["REC", "ERA"]


@pytest.mark.qt
def test_footer_stays_visible_if_left_content_exists_even_when_meta_empty(qtbot):
    bar = FooterBar()
    qtbot.addWidget(bar)
    bar.show()

    bar.add_left(QLabel("LEFT"))
    bar.set_meta("")
    assert not bar.isHidden()


@pytest.mark.qt
def test_panelchrome_set_footer_replaces_right_widget_instead_of_accumulating(qtbot):
    panel = PanelChrome(title="TEST")
    qtbot.addWidget(panel)

    first = QLabel("ONE")
    second = QLabel("TWO")

    panel.set_footer(right_widget=first)
    panel.set_footer(right_widget=second)

    # FooterBar.right_slot: meta label + (optional) extras. Should have only one extra.
    assert panel.footer.right_slot.count() == 2
    assert panel.footer.right_slot.itemAt(1).widget() is second


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
def test_panelchrome_set_filters_and_columns_show_bars_and_clear_hides(qtbot):
    panel = PanelChrome(title="TEST", panel_variant="table")
    qtbot.addWidget(panel)

    assert panel.header_secondary.isHidden()
    assert panel.header_tertiary.isHidden()

    panel.set_filters_left(QLabel("FILTER"))
    assert not panel.header_secondary.isHidden()

    panel.set_columns_left(QLabel("COLS"))
    assert not panel.header_tertiary.isHidden()

    panel.clear_filters()
    assert panel.header_secondary.isHidden()

    panel.clear_columns()
    assert panel.header_tertiary.isHidden()


@pytest.mark.qt
def test_micro_scroll_guard_disables_1px_overflow_and_restores_for_real_overflow(qtbot):
    content = QWidget()
    content.setLayout(QVBoxLayout())
    scroll = make_locked_scroll(content, threshold_px=1, normal_policy=Qt.ScrollBarAsNeeded)
    qtbot.addWidget(scroll)

    scroll.resize(300, 200)
    scroll.show()
    qtbot.waitExposed(scroll)

    viewport_h = scroll.viewport().height()

    # Force a tiny 1px overflow.
    content.setMinimumHeight(viewport_h + 1)
    qtbot.waitUntil(lambda: scroll.verticalScrollBar().maximum() >= 1, timeout=1500)
    qtbot.waitUntil(
        lambda: scroll.verticalScrollBarPolicy() == Qt.ScrollBarAlwaysOff, timeout=1500
    )
    assert scroll.verticalScrollBar().value() == 0
    assert not scroll.verticalScrollBar().isEnabled()

    # Force meaningful overflow; policy should restore.
    content.setMinimumHeight(viewport_h + 80)
    qtbot.waitUntil(lambda: scroll.verticalScrollBar().maximum() > 1, timeout=1500)
    qtbot.waitUntil(
        lambda: scroll.verticalScrollBarPolicy() == Qt.ScrollBarAsNeeded, timeout=1500
    )
    assert scroll.verticalScrollBar().isEnabled()


@pytest.mark.qt
def test_standings_row_click_navigates_to_team_summary(qtbot, monkeypatch, tmp_path):
    """Test standings row click navigation (requires data).
    
    Note: This test now requires actual team data in the repository because
    navigation is ID-based. Without data, the team lookup fails and navigation
    doesn't happen (which is correct behavior).
    """
    root = tmp_path / "app"
    root.mkdir()
    monkeypatch.setenv("GRIDIRONLABS_ROOT", str(root))

    paths = AppPaths.from_env()
    config = load_config(paths, env_file=None)
    logger = logging.getLogger("gridironlabs.ui.test")

    # Create fake team data so navigation can work
    from datetime import date
    import polars as pl
    from gridironlabs.core.models import EntitySummary
    
    processed_dir = paths.data_processed
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a minimal teams.parquet with Buffalo Bills
    teams_data = {
        "id": ["team-buf-2025"],
        "name": ["Buffalo Bills"],
        "entity_type": ["team"],
        "era": ["2025"],
        "team": ["BUF"],
        "ratings": [{"overall": 85.0}],
        "stats": [{"wins": 11.0, "losses": 6.0}],
        "schema_version": ["v0"],
        "source": ["test"],
        "updated_at": [date(2025, 1, 1)],
        "logo_url": [None],
        "logo_path": [None],
    }
    pl.from_dict(teams_data).write_parquet(processed_dir / "teams.parquet")
    
    # Also create empty players/coaches/games so repository doesn't fail
    for table_name in ["players", "coaches"]:
        empty_data = {
            "id": [],
            "name": [],
            "entity_type": [],
            "era": [],
            "team": [],
            "position": [],
            "ratings": [],
            "stats": [],
            "schema_version": [],
            "source": [],
            "updated_at": [],
        }
        pl.from_dict(empty_data).write_parquet(processed_dir / f"{table_name}.parquet")
    
    games_data = {
        "id": [],
        "season": [],
        "week": [],
        "home_team": [],
        "away_team": [],
        "location": [],
        "start_time": [],
        "status": [],
        "is_postseason": [],
        "playoff_round": [],
        "home_score": [],
        "away_score": [],
    }
    pl.from_dict(games_data).write_parquet(processed_dir / "games.parquet")

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


@pytest.mark.qt
def test_standings_header_and_row_share_column_widths(qtbot):
    from PySide6.QtWidgets import QLabel

    from gridironlabs.ui.widgets.standings import STANDINGS_COLUMNS, StandingsHeaderRow

    header = StandingsHeaderRow()
    qtbot.addWidget(header)

    cells = header.findChildren(QLabel, "StandingsHeaderCell")
    assert len(cells) == len(STANDINGS_COLUMNS)
    assert [c.width() for c in cells] == [spec.width for spec in STANDINGS_COLUMNS]

