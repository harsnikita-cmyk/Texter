from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar,
    QLabel,
    QMessageBox,
    QFileDialog,
    QMenu,
    QInputDialog,
    QWidget,
    QVBoxLayout,
    QTextEdit,
)
from PySide6.QtGui import (
    QAction,
    QKeySequence,
    QFont,
    QTextCursor,
    QTextCharFormat,
    QColor,
    QShortcut,
)

from PySide6.QtCore import Qt, QTimer

import os

from file_ops import save_text_to_file, load_text_from_file
from text_editor import TexterEdit, ClickableLabel
from search_bar import SearchBar


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 700)

        self.encoding = "UTF-8"
        self.zoom = 100

        self.current_file: str | None = None
        self.is_modified: bool = False

        self._search_debounce = QTimer(self)
        self._search_debounce.setSingleShot(True)
        self._search_debounce.setInterval(100)
        self._search_debounce.timeout.connect(self._refresh_search)

        self._setup_ui()
        self._update_title()

    def _setup_ui(self):
        self.container = QWidget(self)
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.text_editor = TexterEdit(self)
        font = self.text_editor.font()
        font.setFamily("Calibri")
        font.setPointSize(12)
        self.text_editor.setFont(font)
        self.base_font_size = self.text_editor.font().pointSizeF()
        self.text_editor.textChanged.connect(self._on_text_changed)
        self.text_editor.currentCharFormatChanged.connect(self._sync_format_buttons)
        self.text_editor.selectionChanged.connect(
            lambda: self._sync_format_buttons(self._current_format())
        )

        self.text_editor.cursorPositionChanged.connect(self._on_cursor_moved)

        layout.addWidget(self.text_editor)

        self.search_bar = SearchBar(self)
        self.search_bar.search_requested.connect(self._do_search)
        self.search_bar.next_requested.connect(self._find_next)
        self.search_bar.prev_requested.connect(self._find_prev)
        self.search_bar.replace_requested.connect(self._replace_current)
        self.search_bar.replace_all_requested.connect(self._replace_all)
        self.search_bar.closed.connect(self._hide_search_bar)
        QShortcut(QKeySequence("Escape"), self, self._hide_search_bar)
        self.search_bar.hide()
        layout.addWidget(self.search_bar)

        self.setCentralWidget(self.container)

        self._setup_toolbar()
        self._setup_menu()
        self._setup_status_bar()

    def _on_cursor_moved(self):
        cursor = self.text_editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.positionInBlock() + 1
        self.cursor_position_label.setText(f"{line}:{col}")
        self._sync_format_buttons(self._current_format())

    def _current_format(self):
        cursor = self.text_editor.textCursor()
        if cursor.hasSelection():
            pos = cursor.selectionStart()
            cursor.setPosition(pos)
            cursor.setPosition(pos + 1, QTextCursor.MoveMode.KeepAnchor)
            return cursor.charFormat()
        return self.text_editor.currentCharFormat()

    def _on_text_changed(self):
        self._mark_modified()
        count = len(self.text_editor.toPlainText())
        self.symbols_label.setText(str(count))

        if self.search_bar.isVisible():
            self._search_debounce.start()

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
            self.tool_bar,
            "🔗",
            "Reference",
            checkable=False,
            slot=self._insert_reference,
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
        fmt = self._current_format()
        is_bold = fmt.fontWeight() >= QFont.Weight.Bold
        fmt.setFontWeight(QFont.Weight.Normal if is_bold else QFont.Weight.Bold)
        self.text_editor.mergeCurrentCharFormat(fmt)
        self._mark_modified()

    def _toggle_italic(self):
        fmt = self._current_format()
        fmt.setFontItalic(not fmt.fontItalic())
        self.text_editor.mergeCurrentCharFormat(fmt)
        self._mark_modified()

    def _toggle_underline(self):
        fmt = self._current_format()
        fmt.setFontUnderline(not fmt.fontUnderline())
        self.text_editor.mergeCurrentCharFormat(fmt)
        self._mark_modified()

    def _toggle_strikethrough(self):
        fmt = self._current_format()
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        self.text_editor.mergeCurrentCharFormat(fmt)
        self._mark_modified()

    def _insert_reference(self):
        url, ok = QInputDialog.getText(self, "Insert Link", "URL:")
        if not ok or not url:
            return

        if url.startswith(("http://", "https://")):
            url = "https://" + url

        cursor = self.text_editor.textCursor()
        text = cursor.selectedText() or url

        fmt = QTextCharFormat()
        fmt.setAnchor(True)
        fmt.setAnchorHref(url)
        fmt.setForeground(QColor("#4a9eff"))  # синий, как ссылка
        fmt.setFontUnderline(True)

        cursor.insertText(text, fmt)
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
            slot=self.text_editor.undo,
        )
        self._add_action(
            self.edit_menu,
            "Redo",
            QKeySequence.StandardKey.Redo,
            slot=self.text_editor.redo,
        )
        self.edit_menu.addSeparator()
        self._add_action(
            self.edit_menu,
            "Copy",
            QKeySequence.StandardKey.Copy,
            slot=self.text_editor.copy,
        )
        self._add_action(
            self.edit_menu,
            "Paste",
            QKeySequence.StandardKey.Paste,
            slot=self.text_editor.paste,
        )
        self._add_action(
            self.edit_menu,
            "Cut",
            QKeySequence.StandardKey.Cut,
            slot=self.text_editor.cut,
        )
        self.edit_menu.addSeparator()
        self._add_action(
            self.edit_menu,
            "Select All",
            QKeySequence.StandardKey.SelectAll,
            slot=self.text_editor.selectAll,
        )
        self.edit_menu.addSeparator()
        self._add_action(
            self.edit_menu,
            "Find",
            QKeySequence.StandardKey.Find,
            slot=self._show_search_bar,
        )
        self._add_action(
                    self.edit_menu,
                    "Replace",
                    QKeySequence("Ctrl+H"),
                    slot=self._show_replace_bar,
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

    def _show_search_bar(self):
        self.search_bar.show_replace(False)   # скрыть строку Replace
        self.search_bar.show()
        self.search_bar.search_input.setFocus()
        self.search_bar.search_input.selectAll()

    def _show_replace_bar(self):
        self.search_bar.show_replace(True)    # показать строку Replace
        self.search_bar.show()
        self.search_bar.search_input.setFocus()
        self.search_bar.search_input.selectAll()

    def _hide_search_bar(self):
        if not self.search_bar.isVisible():
            return
        self.search_bar.hide()
        self.text_editor.setExtraSelections([])
        self.text_editor.setFocus()

    def _do_search(self, text: str):
        if not text:
            self.text_editor.setExtraSelections([])
            self.search_bar.match_label.setText("")
            self._match_positions = []
            self._current_match_index = -1
            return

        self._match_positions = self._find_all_matches(text)

        if not self._match_positions:
            self.text_editor.setExtraSelections([])
            self.search_bar.match_label.setText("No results")
            self._current_match_index = -1
            return

        self._current_match_index = 0
        self._highlight_all(text)
        self._jump_to_current_match(text)
        self._update_match_label()

    def _find_all_matches(self, text: str) -> list[int]:
        positions = []
        cursor = QTextCursor(self.text_editor.document())
        while True:
            cursor = self.text_editor.document().find(text, cursor)
            if cursor.isNull():
                break
            positions.append(cursor.selectionStart())
        return positions

    def _find_next(self):
        text = self.search_bar.search_input.text()
        if not text or not self._match_positions:
            return

        self._current_match_index = (self._current_match_index + 1) % len(
            self._match_positions
        )

        self._highlight_all(text)
        self._jump_to_current_match(text)
        self._update_match_label()

    def _find_prev(self):
        text = self.search_bar.search_input.text()
        if not text or not self._match_positions:
            return

        # -1 % 9 == 8 в Python
        self._current_match_index = (self._current_match_index - 1) % len(
            self._match_positions
        )

        self._highlight_all(text)
        self._jump_to_current_match(text)
        self._update_match_label()

    def _jump_to_current_match(self, text: str):
        pos = self._match_positions[self._current_match_index]
        cursor = self.text_editor.textCursor()
        cursor.setPosition(pos)
        cursor.setPosition(pos + len(text), QTextCursor.MoveMode.KeepAnchor)
        self.text_editor.setTextCursor(cursor)
        self.text_editor.ensureCursorVisible()

    def _update_match_label(self):
        total = len(self._match_positions)
        if total == 0:
            self.search_bar.match_label.setText("")
            return
        current = self._current_match_index + 1
        self.search_bar.match_label.setText(f"{current} of {total}")

    def _highlight_all(self, text: str):
        if not text or not self._match_positions:
            self.text_editor.setExtraSelections([])
            return

        normal_fmt = QTextCharFormat()
        normal_fmt.setBackground(QColor("#f0e68c"))
        normal_fmt.setForeground(QColor("#000000"))

        current_fmt = QTextCharFormat()
        current_fmt.setBackground(QColor("#ffa500"))
        current_fmt.setForeground(QColor("#000000"))

        selections = []
        doc = self.text_editor.document()
        for i, pos in enumerate(self._match_positions):
            cursor = QTextCursor(doc)
            cursor.setPosition(pos)
            cursor.setPosition(pos + len(text), QTextCursor.MoveMode.KeepAnchor)

            sel = QTextEdit.ExtraSelection()
            sel.cursor = cursor
            sel.format = current_fmt if i == self._current_match_index else normal_fmt
            selections.append(sel)

        self.text_editor.setExtraSelections(selections)

    def _count_matches(self, text: str) -> int:
        doc = self.text_editor.document()
        cursor = QTextCursor(doc)
        count = 0
        while True:
            cursor = doc.find(text, cursor)
            if cursor.isNull():
                break
            count += 1
        return count

    def _refresh_search(self):
        text = self.search_bar.search_input.text()
        if not text:
            self.text_editor.setExtraSelections([])
            self.search_bar.match_label.setText("")
            self._match_positions = []
            self._current_match_index = -1
            return

        old_index = self._current_match_index
        self._match_positions = self._find_all_matches(text)

        if not self._match_positions:
            self.text_editor.setExtraSelections([])
            self.search_bar.match_label.setText("No results")
            self._current_match_index = -1
            return

        if old_index < 0 or old_index >= len(self._match_positions):
            self._current_match_index = 0
        else:
            self._current_match_index = old_index

        self._highlight_all(text)
        self._update_match_label()

    def _replace_current(self):
        find_text = self.search_bar.search_input.text()
        replace_text = self.search_bar.replace_input.text()

        if not find_text or not self._match_positions:
            return

        # текущее совпадение под курсором?
        pos = self._match_positions[self._current_match_index]

        cursor = self.text_editor.textCursor()
        cursor.setPosition(pos)
        cursor.setPosition(pos + len(find_text), QTextCursor.MoveMode.KeepAnchor)
        self.text_editor.setTextCursor(cursor)

        # заменить
        cursor.insertText(replace_text)

        # пересчитать позиции и подсветку
        self._refresh_search_after_replace(find_text, replace_text)

        # перейти к следующему
        self._find_next()

    def _replace_all(self):
        find_text = self.search_bar.search_input.text()
        replace_text = self.search_bar.replace_input.text()

        if not find_text:
            return

        # защита от бесконечного цикла
        if find_text == replace_text:
            QMessageBox.information(self, "Replace All", "Nothing to replace (same text)")
            return

        # блокируем сигналы редактора чтобы не запускать дебаунс на каждое изменение
        self.text_editor.blockSignals(True)

        # в начало документа
        cursor = self.text_editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.text_editor.setTextCursor(cursor)

        count = 0
        while self.text_editor.find(find_text):
            text_cursor = self.text_editor.textCursor()
            text_cursor.insertText(replace_text)
            count += 1

        # разблокируем сигналы
        self.text_editor.blockSignals(False)

        # пересчитать совпадения
        self._match_positions = self._find_all_matches(find_text)

        if self._match_positions:
            self._current_match_index = 0
            self._highlight_all(find_text)
            self._jump_to_current_match(find_text)
            self._update_match_label()
        else:
            self.text_editor.setExtraSelections([])
            self.search_bar.match_label.setText("")
            self._current_match_index = -1

        # обновить счётчик символов
        self._mark_modified()
        count_chars = len(self.text_editor.toPlainText())
        self.symbols_label.setText(str(count_chars))

        QMessageBox.information(self, "Replace All", f"Replaced: {count}")

    def _refresh_search_after_replace(self, find_text: str, replace_text: str):
        # сохраняем старый индекс
        old_index = self._current_match_index

        # пересчитываем позиции
        self._match_positions = self._find_all_matches(find_text)

        if not self._match_positions:
            self.text_editor.setExtraSelections([])
            self.search_bar.match_label.setText("")
            self._current_match_index = -1
            return

        # индекс не выходит за границы
        if old_index < 0 or old_index >= len(self._match_positions):
            self._current_match_index = 0
        else:
            self._current_match_index = old_index

        self._highlight_all(find_text)
        self._update_match_label()

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

        self.symbols_label = ClickableLabel("0", self.status_bar)
        self.symbols_label.setToolTip("Click for statistics")
        self.symbols_label.clicked.connect(self._show_statistics)
        self.symbols_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.status_bar.addWidget(self.symbols_label)

        self.zoom_label = QLabel(f"{self.zoom}%", self.status_bar)
        self.status_bar.addWidget(self.zoom_label)

    def _show_statistics(self):
        text = self.text_editor.toPlainText()
        doc = self.text_editor.document()

        chars = len(text)
        words = len(text.split())
        paragraphs = doc.blockCount()

        QMessageBox.information(
            self,
            "Statistics",
            f"Symbols: {chars}\nWords: {words}\nParagraphs: {paragraphs}",
        )

    def _new_file(self):
        if not self._maybe_save():
            return

        self.text_editor.clear()
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
        if not save_text_to_file(path, self.text_editor.toHtml()):
            return False

        self.current_file = path
        self.is_modified = False
        self._update_title()
        return True

    def _save_file(self) -> bool:
        if self.current_file is None:
            return self._save_file_as()

        if not save_text_to_file(self.current_file, self.text_editor.toHtml()):
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

        self.text_editor.setHtml(text)
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
        self.text_editor.zoomIn(2)
        self.zoom += 10
        self.zoom_label.setText(f"{str(self.zoom)}%")

    def _zoom_out(self):
        self.text_editor.zoomOut(2)
        self.zoom -= 10
        self.zoom_label.setText(f"{str(self.zoom)}%")

    def _reset_zoom(self):
        font = self.text_editor.font()
        font.setPointSizeF(self.base_font_size)
        self.text_editor.setFont(font)
        self.zoom = 100
        self.zoom_label.setText(f"{self.zoom}%")