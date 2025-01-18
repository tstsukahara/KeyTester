import json
import os

from PyQt5 import QtCore, QtWidgets

from constants import DEFAULT_BASE_DIR, CONF_FILE, IMAGE_DIR


class ConfigManager:
    def __init__(self, parent):
        self.parent = parent
        self.settings = QtCore.QSettings("KeyTester", "Settings")
        self.base_dir = self.settings.value("base_dir", DEFAULT_BASE_DIR)
        self.config_file = os.path.join(self.base_dir, CONF_FILE)
        self.image_dir = os.path.join(self.base_dir, IMAGE_DIR)
        os.makedirs(self.image_dir, exist_ok=True)

    def load_key_map_file(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                return json.load(file)
        return {}

    def save_key_map_file(self, key_map):
        with open(self.config_file, "w") as file:
            json.dump(key_map, file, indent=4)

    def change_base_dir(self):
        new_base_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self.parent, "Select Directory"
        )
        if new_base_dir:
            self.settings.setValue("base_dir", new_base_dir)
            self._update_setting(new_base_dir)
            self.parent.key_info_manager.set_key_map(self.load_key_map_file())

    def _update_setting(self, base_dir):
        self.base_dir = base_dir
        self.config_file = os.path.join(self.base_dir, CONF_FILE)
        self.image_dir = os.path.join(self.base_dir, IMAGE_DIR)
        os.makedirs(self.image_dir, exist_ok=True)
