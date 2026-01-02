"""Rating bar primitives (single and current/potential dual bars)."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget


def _clamp_0_100(value: int | float) -> int:
    try:
        v = int(round(float(value)))
    except Exception:
        v = 0
    return max(0, min(100, v))


def _tier(value: int) -> str:
    # Simple, stable tiers for QSS styling (colors are QSS-first).
    if value >= 70:
        return "elite"
    if value >= 55:
        return "good"
    if value >= 40:
        return "avg"
    return "poor"


@dataclass(frozen=True)
class RatingValue:
    current: int
    potential: int | None = None


class _RatingTrack(QFrame):
    """Track with 1 or 2 fills."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("RatingTrack")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(18)

        self._fill_current = QFrame(self)
        self._fill_current.setObjectName("RatingFillCurrent")

        self._fill_potential = QFrame(self)
        self._fill_potential.setObjectName("RatingFillPotential")
        self._fill_potential.hide()

    def resizeEvent(self, event) -> None:  # type: ignore[override]  # pragma: no cover
        super().resizeEvent(event)
        self._relayout()

    def set_values(self, *, current: int, potential: int | None) -> None:
        self.setProperty("currentTier", _tier(int(current)))
        self.setProperty("potentialTier", _tier(int(potential)) if potential is not None else "none")
        self._fill_potential.setVisible(potential is not None)
        self._current = int(current)
        self._potential = int(potential) if potential is not None else None
        self._relayout()
        self._repolish()

    def _repolish(self) -> None:
        for w in (self, self._fill_current, self._fill_potential):
            w.style().unpolish(w)
            w.style().polish(w)
            w.update()

    def _relayout(self) -> None:
        w = max(1, int(self.width()))
        h = max(1, int(self.height()))
        cur_px = max(0, round((self._current / 100.0) * w))
        self._fill_current.setGeometry(0, 0, cur_px, h)

        if self._potential is None:
            self._fill_potential.setGeometry(0, 0, 0, h)
            return
        pot_px = max(0, round((self._potential / 100.0) * w))
        # Potential is drawn as an extension beyond current.
        start = cur_px
        ext = max(0, pot_px - cur_px)
        self._fill_potential.setGeometry(start, 0, ext, h)


class RatingBarRow(QFrame):
    """Row: label + track + numeric value(s)."""

    def __init__(
        self,
        *,
        label: str,
        current: int,
        potential: int | None = None,
        show_numbers_on_track: bool = True,
    ) -> None:
        super().__init__()
        self.setObjectName("RatingBarRow")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(30)

        self._label = QLabel(label)
        self._label.setObjectName("RatingLabel")
        self._label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self._track = _RatingTrack()

        self._numbers = QLabel()
        self._numbers.setObjectName("RatingNumbers")
        self._numbers.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._numbers.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self._numbers.setFixedWidth(88)

        root = QHBoxLayout(self)
        root.setContentsMargins(10, 0, 10, 0)
        root.setSpacing(10)
        root.addWidget(self._label, 0)
        root.addWidget(self._track, 1)
        root.addWidget(self._numbers, 0)

        self._show_numbers_on_track = bool(show_numbers_on_track)
        self.set_rating(current=current, potential=potential)

    def set_rating(self, *, current: int, potential: int | None = None) -> None:
        cur = _clamp_0_100(current)
        pot = _clamp_0_100(potential) if potential is not None else None
        self.setProperty("ratingVariant", "dual" if pot is not None else "single")

        self._track.set_values(current=cur, potential=pot)

        if pot is None:
            self._numbers.setText(str(cur))
        else:
            self._numbers.setText(f"{cur} / {pot}")

        # Optional: allow styling decisions based on tier.
        self.setProperty("tier", _tier(cur))
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class RatingBarsPanel(QFrame):
    """A simple vertical stack of RatingBarRow widgets."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("RatingBarsPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self._layout = layout

    def add_row(self, row: RatingBarRow) -> None:
        self._layout.addWidget(row)


__all__ = ["RatingBarRow", "RatingBarsPanel", "RatingValue"]

