"""Panel bar primitives (scaffolding).

These bars are the building blocks of the OOTP-style panel contract described in
`recommendation.txt` (repo root).
"""

from __future__ import annotations

from .standard_bars import (
    PanelBar,
    PrimaryHeaderBar,
    SecondaryHeaderBar,
    TertiaryHeaderBar,
    FooterBar,
)

__all__: list[str] = [
    "PanelBar",
    "PrimaryHeaderBar",
    "SecondaryHeaderBar",
    "TertiaryHeaderBar",
    "FooterBar",
]
