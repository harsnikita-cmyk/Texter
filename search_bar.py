from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QToolButton, QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal, QEvent


class SearchBar(QWidget):
    search_requested = Signal(str)
    next_requested = Signal()
    prev_requested = Signal()
    replace_requested = Signal()
    replace_all_requested = Signal()
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # главный вертикальный layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 4, 8, 4)
        main_layout.setSpacing(4)

        # ---------- Строка 1: Find ----------
        find_row = QHBoxLayout()
        find_row.setSpacing(6)

        find_label = QLabel("Find:")
        find_row.addWidget(find_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self.search_requested.emit)
        self.search_input.installEventFilter(self)
        find_row.addWidget(self.search_input, stretch=1)

        self.match_label = QLabel("")
        self.match_label.setMinimumWidth(70)
        self.match_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        find_row.addWidget(self.match_label)

        self.prev_button = QToolButton()
        self.prev_button.setText("↑")
        self.prev_button.setToolTip("Previous (Shift+Enter)")
        self.prev_button.clicked.connect(self.prev_requested.emit)
        find_row.addWidget(self.prev_button)

        self.next_button = QToolButton()
        self.next_button.setText("↓")
        self.next_button.setToolTip("Next (Enter)")
        self.next_button.clicked.connect(self.next_requested.emit)
        find_row.addWidget(self.next_button)

        self.close_button = QToolButton()
        self.close_button.setText("✕")
        self.close_button.setToolTip("Close (Esc)")
        self.close_button.clicked.connect(self.closed.emit)
        find_row.addWidget(self.close_button)

        main_layout.addLayout(find_row)

        # ---------- Строка 2: Replace ----------
        self.replace_row = QWidget()
        replace_layout = QHBoxLayout(self.replace_row)
        replace_layout.setContentsMargins(0, 0, 0, 0)
        replace_layout.setSpacing(6)

        replace_label = QLabel("Replace:")
        replace_layout.addWidget(replace_label)

        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Replace with...")
        replace_layout.addWidget(self.replace_input, stretch=1)

        self.replace_button = QToolButton(self.replace_row)
        self.replace_button.setText("Replace")
        self.replace_button.clicked.connect(self.replace_requested.emit)
        replace_layout.addWidget(self.replace_button)

        self.replace_all_button = QToolButton(self.replace_row)
        self.replace_all_button.setText("Replace All")
        self.replace_all_button.clicked.connect(self.replace_all_requested.emit)
        replace_layout.addWidget(self.replace_all_button)

        main_layout.addWidget(self.replace_row)

        # по умолчанию строка замены скрыта
        self.replace_row.hide()

    def show_replace(self, visible: bool):
        """Показать или скрыть строку замены."""
        self.replace_row.setVisible(visible)

    def is_replace_visible(self) -> bool:
        return self.replace_row.isVisible()

    def eventFilter(self, obj, event):
        if obj is self.search_input and event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    self.prev_requested.emit()
                else:
                    self.next_requested.emit()
                return True
        return super().eventFilter(obj, event)