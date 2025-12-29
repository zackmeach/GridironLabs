"""Centralized UI tokens.

The QSS theme remains the primary source of truth for styling. These tokens exist so
Python-implemented widgets (e.g., debug overlays, layout defaults) share consistent
values and are easy to tune in one place.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ColorTokens:
    """Color constants used by Python-driven UI components."""

    page_bg: str = "#0f1115"
    panel_bg: str = "#252525"
    border: str = "#20242d"
    separator: str = "rgba(255, 255, 255, 0.25)"
    text_primary: str = "#e5e7eb"
    text_secondary: str = "#9ca3af"
    accent: str = "#2563eb"


@dataclass(frozen=True)
class SpacingTokens:
    """Spacing constants shared across pages/panels."""

    page_margins: tuple[int, int, int, int] = (16, 0, 16, 16)
    panel_padding: tuple[int, int, int, int] = (12, 12, 12, 12)
    panel_spacing: int = 10
    grid_gap: int = 12


@dataclass(frozen=True)
class RadiusTokens:
    """Corner radii for common containers."""

    panel_radius: int = 12


@dataclass(frozen=True)
class GridTokens:
    """Defaults for the page content grid and its debug overlay."""

    cols: int = 36
    debug_enabled: bool = False
    debug_opacity: float = 0.18
    debug_cell_size: int = 28
    debug_color_hex: str = "#2563eb"


COLORS = ColorTokens()
SPACING = SpacingTokens()
RADIUS = RadiusTokens()
GRID = GridTokens()
