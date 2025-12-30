"""Panel chrome implementing the OOTP-style container contract.

See `recommendation.txt` for the full spec.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gridironlabs.ui.panels.bars.standard_bars import (
    PrimaryHeaderBar,
    SecondaryHeaderBar,
    TertiaryHeaderBar,
    FooterBar,
)
from gridironlabs.ui.style.tokens import SPACING


class PanelChrome(QFrame):
    """
    OOTP-style panel container.
    
    Structure:
    - Primary Header (Title + Actions)
    - Secondary Header (Filters/Nav)
    - Tertiary Header (Sort/Columns)
    - Body (Content)
    - Footer (Meta)
    """

    def __init__(
        self,
        title: str | None = None,
        *,
        panel_variant: str = "card",
        body_padding: tuple[int, int, int, int] | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("PanelChrome")
        self.setProperty("panelVariant", panel_variant)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Root layout (Vertical stack)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0) # Managed by QSS borders
        self._layout.setSpacing(0)

        # 1. Headers (lazy loaded or optional, but we'll instantiate for structure)
        self.header_primary = PrimaryHeaderBar(title if title else "")
        # Hide if no title, but users might add actions later
        self.header_primary.setVisible(bool(title))
        
        self.header_secondary = SecondaryHeaderBar()
        self.header_secondary.setVisible(False) # Hidden by default until used
        
        self.header_tertiary = TertiaryHeaderBar()
        self.header_tertiary.setVisible(False)

        self._layout.addWidget(self.header_primary)
        self._layout.addWidget(self.header_secondary)
        self._layout.addWidget(self.header_tertiary)

        # 2. Body Container
        self.body_frame = QFrame()
        self.body_frame.setObjectName("PanelBody")
        self._body_layout = QVBoxLayout(self.body_frame)
        resolved_padding: tuple[int, int, int, int]
        if body_padding is not None:
            resolved_padding = body_padding
        elif panel_variant == "table":
            resolved_padding = (0, 0, 0, 0)
        else:
            resolved_padding = SPACING.panel_padding

        self._body_layout.setContentsMargins(*resolved_padding)
        self._body_layout.setSpacing(0)
        
        self._layout.addWidget(self.body_frame, 1) # Stretch factor 1

        # 3. Footer
        self.footer = FooterBar()
        self.footer.setVisible(False)
        self._layout.addWidget(self.footer)
        
    def set_title(self, title: str) -> None:
        self.header_primary.set_title(title)
        self.header_primary.setVisible(True)

    def add_header_action(self, widget: QWidget) -> None:
        """Add action to the primary header (right side)."""
        self.header_primary.add_right(widget)
        self.header_primary.setVisible(True)

    def show_secondary_header(self, visible: bool = True) -> None:
        self.header_secondary.setVisible(visible)

    def show_tertiary_header(self, visible: bool = True) -> None:
        self.header_tertiary.setVisible(visible)

    def set_footer_text(self, text: str) -> None:
        self.footer.set_meta(text)
        self.footer.setVisible(bool(text))

    def set_body(self, widget: QWidget) -> None:
        """Replace body content with a single widget."""
        self.clear_body()
        self._body_layout.addWidget(widget)

    def clear_body(self) -> None:
        """Remove all body content."""
        while self._body_layout.count():
            item = self._body_layout.takeAt(0)
            if w := item.widget():
                w.setParent(None)

    def add_body(self, widget: QWidget, stretch: int = 0) -> None:
        """Add a widget to the body layout."""
        self._body_layout.addWidget(widget, stretch)

    def set_body_padding(self, left: int, top: int, right: int, bottom: int) -> None:
        """Override the body layout padding (useful for table-like panels)."""
        self._body_layout.setContentsMargins(int(left), int(top), int(right), int(bottom))
