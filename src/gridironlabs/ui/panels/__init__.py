"""Panel system scaffolding.

This package is the forward-looking home for the OOTP-style panel system:
- slot-based header/control bars
- semantic section bars
- model/view-friendly bodies

Implementation is intentionally incremental. Today, `PanelChrome` is a thin
compatibility wrapper so the codebase can migrate off legacy `PanelCard`
imports without changing runtime behavior.
"""

from __future__ import annotations

from .panel_chrome import PanelChrome

__all__ = ["PanelChrome"]


