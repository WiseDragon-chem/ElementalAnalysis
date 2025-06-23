import sys
sys.path.append('..')
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.app_controller import AppController

if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = AppController()
    window = MainWindow(controller)
    window.show()
    sys.exit(app.exec_())