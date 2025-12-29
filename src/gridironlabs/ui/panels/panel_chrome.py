"""Panel chrome scaffolding (OOTP-style system).

`PanelChrome` is the new, forward-looking entrypoint for page panels. It will
eventually replace the legacy `PanelCard` with a slot-based control surface
(multiple header bars + semantic section bars + optional footer).

Preparation goal:
- migrate call sites to `PanelChrome` now
- preserve current runtime behavior and styling

See `recommendation.txt` at the repo root for the panel contract.
"""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt

from gridironlabs.ui.style.tokens import SPACING
from gridironlabs.ui.widgets.panel_card import PanelCard


class PanelChrome(PanelCard):
    """Compatibility wrapper around the legacy `PanelCard`.

    This wrapper exists so the codebase can switch imports to `PanelChrome`
    ahead of the panel-system implementation work.
    """

    def __init__(
        self,
        title: str | None = None,
        *,
        link_text: str | None = None,
        on_link_click: Callable[[], None] | None = None,
        show_header: bool = True,
        show_separator: bool = True,
        margins: tuple[int, int, int, int] = SPACING.panel_padding,
        spacing: int = SPACING.panel_spacing,
        title_alignment: Qt.Alignment = Qt.AlignLeft | Qt.AlignTop,
        title_object_name: str = "CardTitlePrimary",
        role: str = "panel",
        panel_variant: str | None = None,
    ) -> None:
        super().__init__(
            title=title,
            link_text=link_text,
            on_link_click=on_link_click,
            show_header=show_header,
            show_separator=show_separator,
            margins=margins,
            spacing=spacing,
            title_alignment=title_alignment,
            title_object_name=title_object_name,
            role=role,
        )

        # New object name (theme.qss maps this to legacy PanelCard styling for now).
        self.setObjectName("PanelChrome")

        if panel_variant:
            self.setProperty("panelVariant", panel_variant)


