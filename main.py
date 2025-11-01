from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.tray.tray import SystemTray
import sys

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    tray = SystemTray(app)
    tray.show()
    app.exec()

if __name__ == "__main__":
    main()