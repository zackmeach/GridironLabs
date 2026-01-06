"""Dev-only panel registry for `scripts/ui_snapshot.py --panel-only ...`.

This allows fast, deterministic iteration on a single panel without requiring full
application navigation.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from gridironlabs.core.models import GameSummary
from gridironlabs.ui.panels import PanelChrome
from gridironlabs.ui.widgets.schedule import LeagueScheduleWidget, ScheduleWeekNavigator


PanelBuilder = Callable[[], QWidget]


def _build_schedule_panel() -> QWidget:
    panel = PanelChrome(title="LEAGUE SCHEDULE", panel_variant="table")
    panel.setObjectName("panel-league-schedule")
    panel.set_footer_text("Tip: Use ◀ ▶ to change weeks.")

    body = LeagueScheduleWidget()
    panel.set_body(body)

    # Deterministic sample dataset (no IO).
    base = datetime(2026, 1, 4, 19, 15, 0)
    sample = [
        GameSummary(
            id="sample-1",
            season=2025,
            week=18,
            home_team="DAL",
            away_team="DET",
            location="AT&T Stadium",
            start_time=base,
            status="scheduled",
            is_postseason=False,
        ),
        GameSummary(
            id="sample-2",
            season=2025,
            week=18,
            home_team="TB",
            away_team="SEA",
            location="Raymond James Stadium",
            start_time=base + timedelta(hours=3),
            status="final",
            is_postseason=False,
            home_score=21,
            away_score=14,
        ),
        GameSummary(
            id="sample-3",
            season=2025,
            week=18,
            home_team="KC",
            away_team="BUF",
            location="Arrowhead Stadium",
            start_time=base + timedelta(days=1, hours=1),
            status="scheduled",
            is_postseason=False,
        ),
    ]
    body.set_games(sample)

    def _prev() -> None:
        body.prev_group()
        nav.set_label(body.current_group_label())

    def _next() -> None:
        body.next_group()
        nav.set_label(body.current_group_label())

    nav = ScheduleWeekNavigator(on_prev=_prev, on_next=_next)
    nav.set_label(body.current_group_label())
    panel.set_primary_right(nav)

    # Tighten focus so keyboard nav doesn't get lost in panel-only window.
    panel.setFocusPolicy(Qt.StrongFocus)
    return panel


def panel_registry() -> dict[str, PanelBuilder]:
    """Map panel objectName -> builder callable."""
    return {
        "panel-league-schedule": _build_schedule_panel,
    }


__all__ = ["PanelBuilder", "panel_registry"]

