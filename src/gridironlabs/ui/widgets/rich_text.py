"""Rich text panel body wrapper (scrollable, link-friendly)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QTextBrowser, QVBoxLayout


class RichTextPanelBody(QFrame):
    def __init__(self, *, html: str = "") -> None:
        super().__init__()
        self.setObjectName("RichTextPanelBody")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.browser = QTextBrowser(self)
        self.browser.setObjectName("RichTextBrowser")
        self.browser.setOpenExternalLinks(True)
        self.browser.setFrameShape(QFrame.NoFrame)
        self.browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.browser.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.browser.setHtml(html)

        layout.addWidget(self.browser)

    def set_html(self, html: str) -> None:
        self.browser.setHtml(html)


__all__ = ["RichTextPanelBody"]

