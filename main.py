from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar,
    QTextEdit,
    QApplication,
    QLabel,
    QMessageBox,
    QMenu,
    QFileDialog
)
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

        self.curent_file: str | None = None
        self.is_modified: bool = False

        self._setup_ui()

    def _setup_ui(self):
        self.text_edit_entry = QTextEdit(self)
        self.text_edit_entry.textChanged.connect(self._on_text_changed)
        self.setCentralWidget(self.text_edit_entry)

        self._setup_toolbar()
        self._setup_menu()
        self._setup_status_bar()

    def _on_text_changed(self):
        self.is_modified=True

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

        self._add_action(self.file_menu, "New", QKeySequence("Ctrl+N"), slot=self._new_file)
        self._add_action(self.file_menu, "Open", QKeySequence("Ctrl+O"))
        self._add_action(self.file_menu, "Save", QKeySequence("Ctrl+S"))
        self._add_action(self.file_menu, "Save As...", QKeySequence("Ctrl+Shift+S"), slot=self._save_file_as)
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

    def _add_action(self, menu: QMenu, text, shortcut, checkable=False, checked=False, slot=None):
        act = QAction(text)
        act.setParent(self)
        if shortcut:
            act.setShortcut(shortcut)
        act.setCheckable(checkable)
        act.setChecked(checked)
        if slot is not None:
            act.triggered.connect(slot)
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

    def _new_file(self):
        if self.is_modified:
            need_save = self._maybe_save()

            if need_save:
                print("Save")
            elif not need_save:
                print("Discard")
            elif need_save is None:
                return

        self.text_edit_entry.clear()

    def _maybe_save(self):
            ask = QMessageBox(self)
            ask.setWindowTitle("Texter")
            ask.setText("Save changes?")
            ask.setIcon(QMessageBox.Icon.Warning)
            ask.setStandardButtons(
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel
            )
            ask.setDefaultButton(QMessageBox.StandardButton.Save)

            result = ask.exec()

            if result == QMessageBox.StandardButton.Save:
                return True
            elif result == QMessageBox.StandardButton.Discard:
                return False
            else:
                return None

    def _save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(
                                                self,
                                                "Save As...",
                                                "",
                                                "Text files (*.txt);;All files (*)")
        with open(path, "wr", encoding="utf-8") as f:
                f.write(self.text_edit_entry.toPlainText())

def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
