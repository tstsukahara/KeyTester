import os

from PyQt5 import QtWidgets

from constants import SWITCH_TYPES, FIELDS


class ChangeDialog(QtWidgets.QDialog):
    def __init__(self, parent, key):
        super().__init__(parent)
        self.parent = parent
        self.key = key
        self.switch_info = self.parent.switch_info_manager.get_switch_info()
        self.switch_name = self.parent.key_info_manager.get_key_map().get(self.key)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Change Switch")
        layout = QtWidgets.QVBoxLayout(self)

        self.select_box = QtWidgets.QComboBox()
        self.select_box.addItems(self.switch_info.keys())
        self.select_box.setCurrentText(self.switch_name)
        layout.addWidget(self.select_box)

        # Saveボタン
        save_button = QtWidgets.QPushButton("Save", self)
        save_button.clicked.connect(self._save)
        layout.addWidget(save_button)

        # Deleteボタン
        delete_button = QtWidgets.QPushButton("Delete", self)
        delete_button.clicked.connect(self._delete)
        layout.addWidget(delete_button)

    def _save(self):
        self._update_switch_name()
        self.parent.key_info_manager.update_key_map(self.key, self.switch_name)
        self.parent.ui_manager.update_display_info(self.key, self.switch_info.get(self.switch_name))
        self.accept()

    def _delete(self):
        self.parent.key_info_manager.delete_key_map(self.key)
        self.parent.ui_manager.update_display_info(self.key, None)
        self.accept()

    def _update_switch_name(self):
        self.switch_name = self.select_box.currentText()