import json
import os

from PyQt5 import QtCore, QtWidgets

from constants import DEFAULT_BASE_DIR, KEY_MAP_FILE, IMAGE_DIR, SWITCH_FILE, DEFAULT_OPEN_DIR


class ConfigManager:
    def __init__(self, parent):
        self.parent = parent
        self.settings = QtCore.QSettings("KeyTester", "Settings")
        self.base_dir = self.settings.value("base_dir", DEFAULT_BASE_DIR)
        self.key_map_file = os.path.join(self.base_dir, KEY_MAP_FILE)
        self.switch_file = os.path.join(self.base_dir, SWITCH_FILE)
        self.image_dir = os.path.join(self.base_dir, IMAGE_DIR)
        self.open_dir =  self.settings.value("open_dir", DEFAULT_OPEN_DIR)
        os.makedirs(self.image_dir, exist_ok=True)

    def load_key_map_file(self):
        if os.path.exists(self.key_map_file):
            with open(self.key_map_file, "r") as file:
                return json.load(file)
        return {}

    def load_switch_file(self):
        if os.path.exists(self.switch_file):
            with open(self.switch_file, "r") as file:
                return json.load(file)
        return {}

    def save_key_map_file(self, key_map):
        with open(self.key_map_file, "w") as file:
            json.dump(key_map, file, indent=4)

    def save_switch_file(self, switch_info):
        with open(self.switch_file, "w") as file:
            json.dump(switch_info, file, indent=4)

    def change_base_dir(self):
        new_base_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self.parent, "Select Directory", DEFAULT_BASE_DIR
        )
        if new_base_dir:
            self.settings.setValue("base_dir", new_base_dir)
            self._update_setting(new_base_dir)
            self.parent.key_map_manager.set_key_map(self.load_key_map_file())

    def _update_setting(self, base_dir):
        self.base_dir = base_dir
        self.key_map_file = os.path.join(self.base_dir, KEY_MAP_FILE)
        self.switch_file = os.path.join(self.base_dir, SWITCH_FILE)
        self.image_dir = os.path.join(self.base_dir, IMAGE_DIR)
        os.makedirs(self.image_dir, exist_ok=True)

    def get_image_dir(self):
        return self.image_dir

    def get_open_dir(self):
        return self.open_dir

    def set_open_dir(self, new_open_dir):
        self.settings.setValue("open_dir", new_open_dir)