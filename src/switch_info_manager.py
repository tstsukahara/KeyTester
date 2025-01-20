import os
import shutil


class SwitchInfoManager:
    def __init__(self, parent):
        self.parent = parent
        self.switch_info = self.parent.config_manager.load_switch_file()

    def get_switch_info(self):
        return self.switch_info

    def set_switch_info(self, switch_info):
        self.switch_info = switch_info

    def update_switch_info(self, switch_name, switch_info):
        self.switch_info[switch_name] = switch_info
        self.parent.config_manager.save_switch_file(self.switch_info)

    def delete_switch_info(self, switch_name):
        self.switch_info.pop(switch_name, None)
        self.parent.config_manager.save_switch_file(self.switch_info)

    def save_image(self, file_path):
        if file_path and os.path.exists(file_path):
            saved_path = os.path.join(
                self.parent.config_manager.get_image_dir(), os.path.basename(file_path)
            )
            shutil.copy(file_path, saved_path)
            return saved_path
        return None
