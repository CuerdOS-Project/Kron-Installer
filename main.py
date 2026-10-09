import sys
import os
import argparse

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from ui.install_win import InstallWin
from ui.styles import global_stylesheet

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_IMAGES_DIR = os.path.join(_BASE_DIR, "images")
_ASSETS_DIR = os.path.join(_BASE_DIR, "ui", "assets")

os.chdir(_BASE_DIR)


def parse_args():
    parser = argparse.ArgumentParser(description="Kron Installer")
    parser.add_argument(
        "--demo",
        dest="demo",
        action="store_true",
        help="ejecuta en modo demo: simula la instalación completa sin "
             "realizar ningún cambio real en el sistema",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    app = QApplication(sys.argv)

    app.setApplicationName("kron-installer")
    app.setDesktopFileName("kron-installer")

    icon_path = os.path.join(_IMAGES_DIR, "kron.svg")
    if os.path.isfile(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Fusion garantiza que QComboBox y otros selectores respeten el QSS
    app.setStyle("Fusion")
    app.setStyleSheet(global_stylesheet(assets_dir=_ASSETS_DIR))

    win = InstallWin(images_dir=_IMAGES_DIR, demo=args.demo)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
