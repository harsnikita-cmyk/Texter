import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from window import Window
import os


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#292929"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#e5e5e5"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#151515"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#2d2d30"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#e5e5e5"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#33333a"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#e5e5e5"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#094771"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2d2d30"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#e5e5e5"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#7f7f7f"))
    palette.setColor(
        QPalette.ColorGroup.Inactive,
        QPalette.ColorRole.WindowText,
        QColor("#9e9e9e"),
    )

    style_path = os.path.join(os.path.dirname(__file__), "styles", "dark_theme.qss")
    with open(style_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    app.setPalette(palette)

    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
