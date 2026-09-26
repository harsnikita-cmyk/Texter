from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QTextEdit


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