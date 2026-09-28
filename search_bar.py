from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QToolButton, QLabel
from PySide6.QtCore import Qt, Signal


class SearchBar(QWidget):
    # Signals
    search_requested = Signal(str)
    next_requested = Signal()
    prev_requested = Signal()
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        find_label = QLabel("Find:")
        layout.addWidget(find_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.returnPressed.connect(self.next_requested.emit)
        self.search_input.textChanged.connect(self.search_requested.emit)
        layout.addWidget(self.search_input, stretch=1)

        self.match_label = QLabel("")
        self.match_label.setMinimumWidth(60)
        self.match_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.match_label)

        self.prev_button = QToolButton()
        self.prev_button.setText("<")
        self.prev_button.setToolTip("Previous (Shift+Enter)")
        self.prev_button.clicked.connect(self.prev_requested.emit)
        layout.addWidget(self.prev_button)

        self.next_button = QToolButton()
        self.next_button.setText(">")
        self.next_button.setToolTip("Next (Enter)")
        self.next_button.clicked.connect(self.next_requested.emit)
        layout.addWidget(self.next_button)

        self.close_button = QToolButton()
        self.close_button.setText("✕")
        self.close_button.setToolTip("Close (Esc)")
        self.close_button.clicked.connect(self.closed.emit)
        layout.addWidget(self.close_button)
