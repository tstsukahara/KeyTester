from PyQt5 import QtWidgets
from PyQt5.QtGui import QKeyEvent

from config_manager import ConfigManager
from constants import VALID_KEYS, DEFAULT_INFO
from edit_dialog import EditDialog
from key_map_manager import KeyMapManager
from src.change_dialog import ChangeDialog
from src.edit_switch_dialog import EditSwitchDialog
from src.switch_info_manager import SwitchInfoManager
from ui_manager import UIManager


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KeyTester")
        self.setGeometry(300, 200, 400, 400)

        self.config_manager = ConfigManager(self)
        self.key_info_manager = KeyMapManager(self)
        self.switch_info_manager = SwitchInfoManager(self)
        self.ui_manager = UIManager(self)
        self.ui_manager.setup_ui()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.text().lower()
        if key in VALID_KEYS:
            self.key_info_manager.set_current_key(key)
            self.ui_manager.hide_label("message")
            self.ui_manager.update_display_info(key, self.switch_info_manager.switch_info.get(self.key_info_manager.key_map.get(key)))
            self.ui_manager.show_edit_button()

    def open_switch_edit(self):
        key = self.key_info_manager.get_current_key()
        dialog = EditSwitchDialog(self, key)
        dialog.exec_()

    def open_change_dialog(self):
        key = self.key_info_manager.get_current_key()
        dialog = ChangeDialog(self, key)
        dialog.exec_()
