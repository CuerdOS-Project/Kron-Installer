import sys
import os
import argparse
import hashlib

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from ui.install_win import InstallWin
from ui.styles import global_stylesheet

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_IMAGES_DIR = os.path.join(_BASE_DIR, "images")
_ASSETS_DIR = os.path.join(_BASE_DIR, "ui", "assets")
_RESOURCES_DIR = os.path.join(_BASE_DIR, "resources")

os.chdir(_BASE_DIR)

# Hash SHA-256 del código secreto de desarrollador requerido para activar
# el modo demo. El código en texto plano NO se almacena en el código fuente
# ni se distribuye públicamente; solo lo conocen los desarrolladores.
_DEV_CODE_HASH = (
    "cb831bb7111e87500d3e853559c89ef73c1111d9169e9b22d4a4050b9e1e2655"
)


def _is_valid_dev_code(code):
    if not code:
        return False
    digest = hashlib.sha256(code.strip().encode("utf-8")).hexdigest()
    return digest == _DEV_CODE_HASH


def parse_args():
    parser = argparse.ArgumentParser(description="Kron Installer")
    parser.add_argument(
        "--dev-code",
        dest="dev_code",
        default=None,
        metavar="CODE",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # El modo demo solo se activa si se proporciona el código secreto
    # exclusivo para desarrolladores. No existe ninguna otra forma de
    # acceder a él (ni flags, ni atajos de teclado, ni variables de
    # entorno alternativas).
    demo_enabled = _is_valid_dev_code(args.dev_code)

    app = QApplication(sys.argv)

    app.setApplicationName("kron-installer")
    app.setDesktopFileName("kron-installer")

    icon_path = os.path.join(_RESOURCES_DIR, "kron.svg")
    if os.path.isfile(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Fusion garantiza que QComboBox y otros selectores respeten el QSS
    app.setStyle("Fusion")
    app.setStyleSheet(global_stylesheet(assets_dir=_ASSETS_DIR))

    win = InstallWin(images_dir=_IMAGES_DIR, demo=demo_enabled)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
