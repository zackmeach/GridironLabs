"""Panel bar primitives (scaffolding).

These bars are the building blocks of the OOTP-style panel contract described in
`docs/UI_CONTRACT.md`.
"""

from __future__ import annotations

from .standard_bars import (
    PanelBar,
    PrimaryHeaderBar,
    SecondaryHeaderBar,
    TertiaryHeaderBar,
    SectionBar,
    FooterBar,
)

__all__: list[str] = [
    "PanelBar",
    "PrimaryHeaderBar",
    "SecondaryHeaderBar",
    "TertiaryHeaderBar",
    "SectionBar",
    "FooterBar",
]
