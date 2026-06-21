import sys
import os

from PySide6.QtWidgets import QApplication

from ui.install_win import InstallWin
from ui.styles import global_stylesheet

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_IMAGES_DIR = os.path.join(_BASE_DIR, "images")
_ASSETS_DIR = os.path.join(_BASE_DIR, "ui", "assets")

os.chdir(_BASE_DIR)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(global_stylesheet(assets_dir=_ASSETS_DIR))
    win = InstallWin(images_dir=_IMAGES_DIR)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()