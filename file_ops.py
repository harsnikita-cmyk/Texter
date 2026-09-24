from PySide6.QtWidgets import QMessageBox


def save_text_to_file(path: str, text: str) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    except OSError as e:
        QMessageBox.critical(None, "Error", f"Cannot save file:\n{e}")
        return False


def load_text_from_file(path: str) -> str | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        QMessageBox.critical(None, "Error", f"Cannot open file:\n{e}")
        return None