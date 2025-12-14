"""Deprecated compatibility wrapper for the legacy PanelCard API."""

from __future__ import annotations

from PySide6.QtCore import Qt

from gridironlabs.ui.widgets.base_components import Card


class PanelCard(Card):
    """Alias for Card kept to avoid import breakage."""

    def __init__(
        self,
        title: str | None = None,
        *,
        margins: tuple[int, int, int, int] = (12, 12, 12, 12),
        spacing: int = 10,
        show_separator: bool = True,
        title_alignment: Qt.Alignment = Qt.AlignLeft | Qt.AlignTop,
    ) -> None:
        super().__init__(
            title=title,
            role="primary",
            margins=margins,
            spacing=spacing,
            show_separator=show_separator,
            title_alignment=title_alignment,
        )

