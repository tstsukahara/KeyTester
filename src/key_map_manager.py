import os
import shutil


class KeyMapManager:
    def __init__(self, parent):
        self.parent = parent
        self.key_map = self.parent.config_manager.load_key_map_file()
        self.switch_info = self.parent.config_manager.load_switch_file()
        self.current_key = None

    def get_current_key(self):
        return self.current_key

    def set_current_key(self, key):
        self.current_key = key

    def get_key_map(self):
        return self.key_map

    def set_key_map(self, key_map):
        self.key_map = key_map

    def update_key_map(self, key, key_info):
        self.key_map[key] = key_info
        self.parent.config_manager.save_key_map_file(self.key_map)

    def delete_key_map(self, key):
        self.key_map.pop(key, None)
        self.parent.config_manager.save_key_map_file(self.key_map)

    def save_image(self, file_path):
        if file_path and os.path.exists(file_path):
            saved_path = os.path.join(self.parent.config_manager.get_image_dir(), os.path.basename(file_path))
            shutil.copy(file_path, saved_path)
            return saved_path
        return None
