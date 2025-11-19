from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QStackedWidget)

class PeopleInterface(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)