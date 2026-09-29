from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtWidgets import QTextEdit, QLabel


class TexterEdit(QTextEdit):
    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            pos = event.position().toPoint()
            cursor = self.cursorForPosition(pos)
            anchor = cursor.charFormat().anchorHref()

            if anchor:
                # добавляем протокол если нет
                if not anchor.startswith(("http://", "https://")):
                    anchor = "https://" + anchor

                QDesktopServices.openUrl(QUrl(anchor))


class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        self.clicked.connect if False else None  # dummy
        self.clicked.emit()
        super().mousePressEvent(event)
