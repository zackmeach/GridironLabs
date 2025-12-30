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

    def __init__(self, title: str | None = None) -> None:
        super().__init__()
        self.setObjectName("PanelChrome")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Root layout (Vertical stack)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(1, 1, 1, 1) # Border thickness space
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
        self.body_layout = QVBoxLayout(self.body_frame)
        self.body_layout.setContentsMargins(12, 12, 12, 12) # Standard padding
        self.body_layout.setSpacing(0)
        
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
