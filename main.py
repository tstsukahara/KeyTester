"""メインモジュール"""

from PyQt5 import QtWidgets
import sys
from KeyTester import KeyTester


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = KeyTester()
    window.show()
    sys.exit(app.exec_())
