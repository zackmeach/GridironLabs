
import sys
import os
sys.path.insert(0, os.path.abspath('src'))

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from gridironlabs.ui.widgets.panel_card import PanelCard
from gridironlabs.ui.style.tokens import SPACING

def inspect_card_layout():
    app = QApplication.instance() or QApplication(sys.argv)
    
    card = PanelCard("test CaRd")
    card.resize(400, 300)
    card.show()
    app.processEvents()
    
    title_lbl = card.title_label
    header_stack = card._header_stack
    separator = card._separator
    
    # Global positions
    title_pos = title_lbl.mapTo(card, title_lbl.rect().topLeft())
    stack_pos = header_stack.mapTo(card, header_stack.rect().topLeft())
    
    print(f"--- Layout Inspection ---")
    print(f"Card Height: {card.height()}px")
    print(f"Header Stack Y: {stack_pos.y()}px")
    print(f"Header Stack Height: {header_stack.height()}px")
    print(f"Title Top Y: {title_pos.y()}px")
    
    # Check alignment
    if stack_pos.y() > 20: # Allow for margins (12px)
        print("FAIL: Header stack is NOT at the top of the card!")
    else:
        print("PASS: Header stack is at the top.")

if __name__ == "__main__":
    inspect_card_layout()
