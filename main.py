import sys
from PySide6.QtWidgets import QApplication
from ui.install_win import InstallWin

def main():
    app = QApplication(sys.argv)
    win = InstallWin()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()