 from __future__ import annotations
 
from PySide6 import QtCore, QtWidgets
 
 
 class NavigationBar(QtWidgets.QWidget):
     """
     Top navigation bar inspired by OOTP26 layout.
     """
 
     back_requested = QtCore.Signal()
     forward_requested = QtCore.Signal()
     home_requested = QtCore.Signal()
     search_requested = QtCore.Signal(str)
 
     def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
         super().__init__(parent)
         self._build_ui()
 
     def _build_ui(self) -> None:
         self.setObjectName("navigationBar")
 
         layout = QtWidgets.QHBoxLayout(self)
         layout.setContentsMargins(8, 8, 8, 8)
         layout.setSpacing(8)
 
         self.back_button = QtWidgets.QToolButton(text="◀")
         self.forward_button = QtWidgets.QToolButton(text="▶")
         self.home_button = QtWidgets.QToolButton(text="🏠")
         self.search_field = QtWidgets.QLineEdit()
         self.search_field.setPlaceholderText("Search players, teams, coaches")
 
         layout.addWidget(self.back_button)
         layout.addWidget(self.forward_button)
         layout.addWidget(self.home_button)
         layout.addSpacing(12)
         layout.addWidget(self.search_field, 1)
 
         # Wire signals
         self.back_button.clicked.connect(self.back_requested.emit)
         self.forward_button.clicked.connect(self.forward_requested.emit)
         self.home_button.clicked.connect(self.home_requested.emit)
         self.search_field.returnPressed.connect(self._emit_search)
 
     @QtCore.Slot()
     def _emit_search(self) -> None:
         self.search_requested.emit(self.search_field.text())
