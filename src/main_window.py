from PyQt5 import QtWidgets
from PyQt5.QtGui import QKeyEvent

from config_manager import ConfigManager
from constants import VALID_KEYS, DEFAULT_INFO
from edit_dialog import EditDialog
from key_info_manager import KeyInfoManager
from ui_manager import UIManager


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KeyTester")
        self.setGeometry(300, 200, 400, 400)

        self.config_manager = ConfigManager(self)
        self.key_info_manager = KeyInfoManager(self)
        self.ui_manager = UIManager(self)

        self.ui_manager.setup_ui()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.text().lower()
        if key in VALID_KEYS:
            self.key_info_manager.set_current_key(key)
            self.ui_manager.hide_label("message")
            self.ui_manager.update_display_info(key, self.key_info_manager.key_map.get(key))
            self.ui_manager.show_edit_button()

    def open_edit(self):
        key = self.key_info_manager.get_current_key()
        key_info = self.key_info_manager.get_key_map().get(key, DEFAULT_INFO.copy())
        dialog = EditDialog(self, key, key_info)
        dialog.exec_()