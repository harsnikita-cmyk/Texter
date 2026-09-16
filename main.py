from PySide6.QtWidgets import QMainWindow, QToolBar, QTextEdit, QApplication, QLabel
from PySide6.QtGui import QAction, QKeySequence
import sys


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Texter")
        self.resize(1000, 700)

        self.cursor_position = "0:0"
        self.encoding = "UTF-8"
        self.symbols = 0
        self.zoom = 100

        self._setup_ui()

    def _setup_ui(self):
        self.text_edit_entry = QTextEdit(self)
        self.setCentralWidget(self.text_edit_entry)

        self._setup_toolbar()
        self._setup_menu()
        self._setup_status_bar()

    def _setup_toolbar(self):
        self.tool_bar = QToolBar(self)
        self._add_toolbar_action(self.tool_bar, "B", "Bold", checkable=True)
        self._add_toolbar_action(self.tool_bar, "I", "Italic", checkable=True)
        self._add_toolbar_action(self.tool_bar, "U", "Underline", checkable=True)
        self.tool_bar.addSeparator()
        self._add_toolbar_action(self.tool_bar, "S", "Crossed", checkable=True)
        self._add_toolbar_action(self.tool_bar, "R", "Reference", checkable=False)
        self.tool_bar.setMovable(False)
        self.addToolBar(self.tool_bar)
    def _add_toolbar_action(self, toolbar: QToolBar, text, tooltip, checkable=False):
        act = QAction(text, self)
        act.setToolTip(tooltip)
        act.setCheckable(checkable)
        toolbar.addAction(act)
        return act

    def _setup_menu(self):
        self.menu_bar = self.menuBar()

        self.file_menu = self.menu_bar.addMenu("File")

        self._add_action(self.file_menu, "New", QKeySequence("Ctrl+N"))
        self._add_action(self.file_menu, "Open", QKeySequence("Ctrl+O"))
        self._add_action(self.file_menu, "Save", QKeySequence("Ctrl+S"))
        self._add_action(self.file_menu, "Save As...", QKeySequence("Ctrl+Shift+S"))
        self.file_menu.addSeparator()
        self._add_action(self.file_menu, "Print", QKeySequence("Ctrl+P"))
        self.file_menu.addSeparator()
        self._add_action(self.file_menu, "Quit", QKeySequence("Ctrl+Q"))

        self.edit_menu = self.menu_bar.addMenu("Edit")

        self._add_action(self.edit_menu, "Undo", QKeySequence("Ctrl+Z"))
        self._add_action(self.edit_menu, "Redo", QKeySequence("Ctrl+Shift+Z"))
        self.edit_menu.addSeparator()
        self._add_action(self.edit_menu, "Copy", QKeySequence("Ctrl+C"))
        self._add_action(self.edit_menu, "Paste", QKeySequence("Ctrl+V"))
        self._add_action(self.edit_menu, "Cut", QKeySequence("Ctrl+X"))
        self.edit_menu.addSeparator()
        self._add_action(self.edit_menu, "Select All", QKeySequence("Ctrl+A"))

        self.view_menu = self.menu_bar.addMenu("View")

        self._add_action(self.view_menu, "Zoom In", QKeySequence("Ctrl++"))
        self._add_action(self.view_menu, "Zoom Out", QKeySequence("Ctrl+-"))
        self.view_menu.addSeparator()
        self._add_action(self.view_menu, "Reset Zoom", QKeySequence("Ctrl+0"))

        self.reference_menu = self.menu_bar.addMenu("Reference")
        self._add_action(self.reference_menu, "About Texter", QKeySequence("F1"))
    def _add_action(self, menu, text, shortcut, checkable=False, checked=False):
        act = QAction(text)
        act.setParent(self)
        if shortcut:
            act.setShortcut(shortcut)
        act.setCheckable(checkable)
        act.setChecked(checked)
        menu.addAction(act)
        return act

    def _setup_status_bar(self):
        self.status_bar = self.statusBar()

        self.cursor_position_label = QLabel(self.cursor_position, self.status_bar)
        self.status_bar.addWidget(self.cursor_position_label)

        self.encoding_label = QLabel(self.encoding, self.status_bar)
        self.status_bar.addWidget(self.encoding_label)

        self.symbols_label = QLabel(str(self.symbols), self.status_bar)
        self.status_bar.addWidget(self.symbols_label)

        self.zoom_label = QLabel(f"{self.zoom}%", self.status_bar)
        self.status_bar.addWidget(self.zoom_label)

def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()