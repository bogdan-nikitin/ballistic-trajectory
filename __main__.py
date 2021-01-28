import sys
import locale
from PyQt5.QtWidgets import QApplication

from programwindow import ProgramWindow

if __name__ == '__main__':
    locale.setlocale(locale.LC_NUMERIC, '')
    app = QApplication(sys.argv)
    ex = ProgramWindow()
    ex.show()
    sys.exit(app.exec_())
