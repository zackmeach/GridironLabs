"""Chart panel body wrapper.

Chart rendering tech is an explicit open decision. For now this wrapper simply
hosts an injected chart widget (QtCharts, matplotlib canvas, etc.).
"""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget


class ChartPanelBody(QFrame):
    def __init__(self, *, chart_widget: QWidget | None = None) -> None:
        super().__init__()
        self.setObjectName("ChartPanelBody")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        if chart_widget is not None:
            chart_widget.setParent(self)
            layout.addWidget(chart_widget)

    def set_chart(self, widget: QWidget) -> None:
        # Replace body content.
        while self.layout().count():  # type: ignore[union-attr]
            item = self.layout().takeAt(0)  # type: ignore[union-attr]
            if w := item.widget():
                w.setParent(None)
        widget.setParent(self)
        self.layout().addWidget(widget)  # type: ignore[union-attr]


__all__ = ["ChartPanelBody"]

