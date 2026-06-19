import sys, os
from PySide6.QtWidgets import QApplication
from ui.install_win import InstallWin
from ui.styles import global_stylesheet

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(global_stylesheet())
    win = InstallWin()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
