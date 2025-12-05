 from __future__ import annotations
 
from pathlib import Path

from PySide6 import QtCore, QtWidgets
 
 from gridironlabs.services.search_service import SearchService
 from gridironlabs.ui.widgets.navigation_bar import NavigationBar
 
 
 class MainWindow(QtWidgets.QMainWindow):
     """
     Application shell with persistent top navigation bar and stacked views.
     """
 
     def __init__(self, search_service: SearchService, parent: QtWidgets.QWidget | None = None):
         super().__init__(parent)
         self.search_service = search_service
         self.setWindowTitle("Gridiron Labs")
         self.resize(1280, 800)
         self._build_ui()
 
     def _build_ui(self) -> None:
         central = QtWidgets.QWidget(self)
         main_layout = QtWidgets.QVBoxLayout(central)
         main_layout.setContentsMargins(0, 0, 0, 0)
         main_layout.setSpacing(0)
 
         self.nav_bar = NavigationBar(self)
         self.nav_bar.search_requested.connect(self._on_search)
         main_layout.addWidget(self.nav_bar)
 
         self.stack = QtWidgets.QStackedWidget(self)
         self.home_page = self._build_home_placeholder()
         self.stack.addWidget(self.home_page)
         main_layout.addWidget(self.stack, 1)
 
         self.setCentralWidget(central)
 
     def _build_home_placeholder(self) -> QtWidgets.QWidget:
         widget = QtWidgets.QWidget(self)
         layout = QtWidgets.QVBoxLayout(widget)
         layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
 
         hero = QtWidgets.QLabel("Gridiron Labs")
         hero.setObjectName("heroTitle")
         hero.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
         subtitle = QtWidgets.QLabel("NFL analytics inspired by OOTP26")
         subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
 
         layout.addStretch()
         layout.addWidget(hero)
         layout.addWidget(subtitle)
         layout.addStretch()
         return widget
 
     @QtCore.Slot(str)
     def _on_search(self, query: str) -> None:
         results = self.search_service.search(query)
         message = "\n".join(f"{r.entity_type}: {r.name}" for r in results) or "No matches yet."
         QtWidgets.QMessageBox.information(self, "Search", message)
 
 
 def load_stylesheet(path: Path) -> str:
     try:
         return path.read_text(encoding="utf-8")
     except FileNotFoundError:
         return ""
