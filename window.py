from PySide6.QtWidgets import (
    QMainWindow,
    QTextEdit,
    QToolBar,
    QLabel,
    QMessageBox,
    QFileDialog,
    QMenu,
)
from PySide6.QtGui import QAction, QKeySequence, QFont, QTextCursor

import os

from file_ops import save_text_to_file, load_text_from_file


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 700)

        self.encoding = "UTF-8"
        self.zoom = 100

        self.current_file: str | None = None
        self.is_modified: bool = False

        self._setup_ui()
        self._update_title()

    def _setup_ui(self):
        self.text_edit_entry = QTextEdit(self)
        self.base_font_size = self.text_edit_entry.font().pointSizeF()
        self.text_edit_entry.textChanged.connect(self._on_text_changed)
        self.text_edit_entry.currentCharFormatChanged.connect(self._sync_format_buttons)
        self.text_edit_entry.selectionChanged.connect(
            lambda: self._sync_format_buttons(self._current_format())
        )

        self.text_edit_entry.cursorPositionChanged.connect(self._on_cursor_moved)

        self.setCentralWidget(self.text_edit_entry)

        self._setup_toolbar()
        self._setup_menu()
        self._setup_status_bar()

    def _on_cursor_moved(self):
        cursor = self.text_edit_entry.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.positionInBlock() + 1
        self.cursor_position_label.setText(f"{line}:{col}")
        self._sync_format_buttons(self._current_format())

    def _current_format(self):
        cursor = self.text_edit_entry.textCursor()
        if cursor.hasSelection():
            pos = cursor.selectionStart()
            cursor.setPosition(pos)
            cursor.setPosition(pos + 1, QTextCursor.MoveMode.KeepAnchor)
            return cursor.charFormat()
        return self.text_edit_entry.currentCharFormat()

    def _on_text_changed(self):
        self._mark_modified()

        count = len(self.text_edit_entry.toPlainText())
        self.symbols_label.setText(str(count))

    def _mark_modified(self):
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
        self.bold_button = self._add_toolbar_action(
            self.tool_bar,
            "B",
            "Bold",
            checkable=True,
            style="bold",
            slot=self._toggle_bold,
        )
        self.italic_button = self._add_toolbar_action(
            self.tool_bar,
            "I",
            "Italic",
            checkable=True,
            style="italic",
            slot=self._toggle_italic,
        )
        self.underline_button = self._add_toolbar_action(
            self.tool_bar,
            "U",
            "Underline",
            checkable=True,
            style="underline",
            slot=self._toggle_underline,
        )
        self.tool_bar.addSeparator()
        self.strikethrough_button = self._add_toolbar_action(
            self.tool_bar,
            "S",
            "Strikethrough",
            checkable=True,
            style="strike",
            slot=self._toggle_strikethrough,
        )
        self.reference_button = self._add_toolbar_action(
            self.tool_bar, "🔗", "Reference", checkable=False
        )
        self.tool_bar.setMovable(False)
        self.addToolBar(self.tool_bar)

    def _add_toolbar_action(
        self, toolbar, text, tooltip, checkable=False, style=None, slot=None
    ):
        act = QAction(text)
        act.setParent(self)
        act.setToolTip(tooltip)
        act.setCheckable(checkable)

        if style:
            font = act.font()
            if style == "bold":
                font.setBold(True)
            elif style == "italic":
                font.setItalic(True)
            elif style == "underline":
                font.setUnderline(True)
            elif style == "strike":
                font.setStrikeOut(True)
            font.setPointSize(font.pointSize() + 4)
            act.setFont(font)

        if slot is not None:
            act.triggered.connect(slot)

        toolbar.addAction(act)
        return act

    def _toggle_bold(self):
        fmt = self.text_edit_entry.currentCharFormat()
        is_bold = fmt.fontWeight() >= QFont.Weight.Bold
        fmt.setFontWeight(QFont.Weight.Normal if is_bold else QFont.Weight.Bold)
        self.text_edit_entry.mergeCurrentCharFormat(fmt)
        self._mark_modified()

    def _toggle_italic(self):
        fmt = self.text_edit_entry.currentCharFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        self.text_edit_entry.mergeCurrentCharFormat(fmt)
        self._mark_modified()

    def _toggle_underline(self):
        fmt = self.text_edit_entry.currentCharFormat()
        fmt.setFontUnderline(not fmt.fontUnderline())
        self.text_edit_entry.mergeCurrentCharFormat(fmt)
        self._mark_modified()

    def _toggle_strikethrough(self):
        fmt = self.text_edit_entry.currentCharFormat()
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        self.text_edit_entry.mergeCurrentCharFormat(fmt)
        self._mark_modified()

    def _sync_format_buttons(self, fmt):
        is_bold = fmt.fontWeight() >= QFont.Weight.Bold
        for button, checked in (
            (self.bold_button, is_bold),
            (self.italic_button, fmt.fontItalic()),
            (self.underline_button, fmt.fontUnderline()),
            (self.strikethrough_button, fmt.fontStrikeOut()),
        ):
            button.blockSignals(True)
            button.setChecked(checked)
            button.blockSignals(False)

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

        self._add_action(
            self.view_menu,
            "Zoom In",
            QKeySequence.StandardKey.ZoomIn,
            slot=self._zoom_in,
        )
        self._add_action(
            self.view_menu,
            "Zoom Out",
            QKeySequence.StandardKey.ZoomOut,
            slot=self._zoom_out,
        )
        self.view_menu.addSeparator()
        self._add_action(
            self.view_menu, "Reset Zoom", QKeySequence("Ctrl+0"), slot=self._reset_zoom
        )

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

        self.cursor_position_label = QLabel("1:1", self.status_bar)
        self.status_bar.addWidget(self.cursor_position_label)

        self.encoding_label = QLabel(self.encoding, self.status_bar)
        self.status_bar.addWidget(self.encoding_label)

        self.symbols_label = QLabel("0", self.status_bar)
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
        path, _ = QFileDialog.getSaveFileName(  # ← ВОТ ЗДЕСЬ path появлялся
            self, "Save As...", "", "Text files (*.txt);;All files (*)"
        )
        if not path:
            return False
        if not save_text_to_file(path, self.text_edit_entry.toPlainText()):
            return False

        self.current_file = path
        self.is_modified = False
        self._update_title()
        return True

    def _save_file(self) -> bool:
        if self.current_file is None:
            return self._save_file_as()

        if not save_text_to_file(self.current_file, self.text_edit_entry.toPlainText()):
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

        text = load_text_from_file(path)
        if text is None:
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

    def _zoom_in(self):
        self.text_edit_entry.zoomIn(2)
        self.zoom += 10
        self.zoom_label.setText(f"{str(self.zoom)}%")

    def _zoom_out(self):
        self.text_edit_entry.zoomOut(2)
        self.zoom -= 10
        self.zoom_label.setText(f"{str(self.zoom)}%")

    def _reset_zoom(self):
        font = self.text_edit_entry.font()
        font.setPointSizeF(self.base_font_size)
        self.text_edit_entry.setFont(font)
        self.zoom = 100
        self.zoom_label.setText(f"{self.zoom}%")
