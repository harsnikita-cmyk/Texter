from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar,
    QTextEdit,
    QApplication,
    QLabel,
    QMessageBox,
    QMenu,
    QFileDialog,
)
from PySide6.QtGui import QAction, QKeySequence
import sys
import os


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 700)

        self.cursor_position = "0:0"
        self.encoding = "UTF-8"
        self.symbols = 0
        self.zoom = 100

        self.current_file: str | None = None
        self.is_modified: bool = False

        self._setup_ui()
        self._update_title()

    def _setup_ui(self):
        self.text_edit_entry = QTextEdit(self)
        self.text_edit_entry.textChanged.connect(self._on_text_changed)
        self.setCentralWidget(self.text_edit_entry)

        self._setup_toolbar()
        self._setup_menu()
        self._setup_status_bar()

    def _on_text_changed(self):
        if not self.is_modified:
            self.is_modified = True
            self._update_title()

    def closeEvent(self, event):
        if self._maybe_save():
            event.accept()
        else:
            event.ignore()

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
        act = QAction(text)
        act.setParent(self)
        act.setToolTip(tooltip)
        act.setCheckable(checkable)
        toolbar.addAction(act)
        return act

    def _setup_menu(self):
        self.menu_bar = self.menuBar()

        self.file_menu = self.menu_bar.addMenu("File")

        self._add_action(
            self.file_menu, "New", QKeySequence.StandardKey.New, slot=self._new_file
        )

        self._add_action(
            self.file_menu, "Open", QKeySequence.StandardKey.Open, slot=self._open_file
        )

        self._add_action(
            self.file_menu, "Save", QKeySequence.StandardKey.Save, slot=self._save_file
        )

        self._add_action(
            self.file_menu,
            "Save As...",
            QKeySequence.StandardKey.SaveAs,
            slot=self._save_file_as,
        )

        self.file_menu.addSeparator()

        self._add_action(self.file_menu, "Print", QKeySequence.StandardKey.Print)

        self.file_menu.addSeparator()

        self._add_action(
            self.file_menu,
            "Quit",
            QKeySequence.StandardKey.Quit,
            slot=self.close,
        )

        self.edit_menu = self.menu_bar.addMenu("Edit")

        self._add_action(
            self.edit_menu,
            "Undo",
            QKeySequence.StandardKey.Undo,
            slot=self.text_edit_entry.undo,
        )
        self._add_action(
            self.edit_menu,
            "Redo",
            QKeySequence.StandardKey.Redo,
            slot=self.text_edit_entry.redo,
        )
        self.edit_menu.addSeparator()
        self._add_action(
            self.edit_menu,
            "Copy",
            QKeySequence.StandardKey.Copy,
            slot=self.text_edit_entry.copy,
        )
        self._add_action(
            self.edit_menu,
            "Paste",
            QKeySequence.StandardKey.Paste,
            slot=self.text_edit_entry.paste,
        )
        self._add_action(
            self.edit_menu,
            "Cut",
            QKeySequence.StandardKey.Cut,
            slot=self.text_edit_entry.cut,
        )
        self.edit_menu.addSeparator()
        self._add_action(
            self.edit_menu,
            "Select All",
            QKeySequence.StandardKey.SelectAll,
            slot=self.text_edit_entry.selectAll,
        )

        self.view_menu = self.menu_bar.addMenu("View")

        self._add_action(self.view_menu, "Zoom In", QKeySequence.StandardKey.ZoomIn)
        self._add_action(self.view_menu, "Zoom Out", QKeySequence.StandardKey.ZoomOut)
        self.view_menu.addSeparator()
        self._add_action(self.view_menu, "Reset Zoom", QKeySequence("Ctrl+0"))

        self.reference_menu = self.menu_bar.addMenu("Reference")
        self._add_action(
            self.reference_menu, "About Texter", QKeySequence("F1"), slot=self._about
        )

    def _add_action(
        self, menu: QMenu, text, shortcut, checkable=False, checked=False, slot=None
    ):
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
        if not self._maybe_save():
            return

        self.text_edit_entry.clear()
        self.current_file = None
        self.is_modified = False
        self._update_title()

    def _maybe_save(self):
        if not self.is_modified:
            return True

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
            return self._save_file()
        elif result == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False

    def _save_file_as(self) -> bool:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save As...", "", "Text files (*.txt);;All files (*)"
        )
        if not path:
            return False

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text_edit_entry.toPlainText())
        except OSError as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{e}")
            return False

        self.current_file = path  # ← ЗАПОМНИТЬ путь
        self.is_modified = False  # ← СБРОСИТЬ флаг
        self._update_title()  # ← ОБНОВИТЬ заголовок
        return True

    def _save_file(self) -> bool:
        if self.current_file is None:
            return self._save_file_as()

        try:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.text_edit_entry.toPlainText())
        except OSError as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{e}")
            return False

        self.is_modified = False
        self._update_title()
        return True

    def _open_file(self):
        if not self._maybe_save():
            return

        path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Text Files (*.txt);;All files (*)"
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть:\n{e}")
            return

        self.text_edit_entry.setPlainText(text)
        self.current_file = path
        self.is_modified = False
        self._update_title()

    def _update_title(self):
        name = os.path.basename(self.current_file) if self.current_file else "New"
        star = " *" if self.is_modified else ""
        self.setWindowTitle(f"Texter - {name}{star}")

    def _about(self):
        QMessageBox.about(
            self,
            "About Texter",
            "Texter 1.0.\n"
            "Simple text editor.\n"
            "Written in Python, with the graphical part in PySide6.\n"
            "Author: CMYKNIK.",
        )


def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
