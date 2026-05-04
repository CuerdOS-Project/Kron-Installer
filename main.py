import sys
from PySide6.QtWidgets import QApplication
from ui.install_win import InstallWin
from ui.styles import global_stylesheet

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(global_stylesheet())
    win = InstallWin()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
