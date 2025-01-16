import shutil
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QRectF
import sys
import json
import os

from PyQt5.QtGui import QPixmap, QPainter, QPainterPath

QWERT_KEYS = r"1234567890-=qwertyuiop[]\asdfghjkl;'zxcvbnm,./"
SWITCH_TYPES = ["-", "Linear", "Tactile", "Clicky", "Silent Linear", "Silent Tactile", "Silent Clicky",]
DEFAULT_INFO = {
    "default": {
        "image": "",
        "switch_name": "-",
        "switch_type": "-",
        "operation_force": "-",
        "link": "-"
    }
}

class KeyTesterApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KeyTester")
        self.setGeometry(300, 200, 400, 400)

        # 設定ファイルの読み込み
        self.settings = QtCore.QSettings("KeyTester", "Settings")
        default_base_dir = os.path.join(os.environ["HOME"], "Documents/KeyTester")
        self.base_dir = self.settings.value("base_dir", default_base_dir)
        self.config_file = os.path.join(self.base_dir, "key_map.json")
        self.image_dir = os.path.join(self.base_dir, "images")
        os.makedirs(self.image_dir, exist_ok=True)
        self.key_map = self.load_key_map()

        # メニューバーの作成
        menubar = self.menuBar()
        setting_menu = menubar.addMenu('Settings')
        change_base_dir_action = QtWidgets.QAction("Change Base Directory", self)
        change_base_dir_action.triggered.connect(self.change_base_dir)
        setting_menu.addAction(change_base_dir_action)

        # キーの初期化
        self.key = QWERT_KEYS[0]

        # レイアウトの作成
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(central_widget)

        # キー
        self.key_layout = QtWidgets.QHBoxLayout()
        self.key_label = QtWidgets.QLabel(self)
        self.key_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.key_label)

        # メッセージ表示
        self.message_label = QtWidgets.QLabel("Press any key.")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.message_label)

        # 画像
        self.image_layout = QtWidgets.QVBoxLayout()
        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_layout.addWidget(self.image_label)
        self.main_layout.addLayout(self.image_layout)
        self.is_image_updated = False

        # 名前
        self.switch_name_layout = QtWidgets.QHBoxLayout()
        self.switch_name = QtWidgets.QLabel("", self)
        self.switch_name.setStyleSheet("font-weight: bold;")
        self.switch_name.setStyleSheet("font: 20px;")
        self.switch_name.setAlignment(Qt.AlignCenter)
        self.switch_name_layout.addWidget(self.switch_name)
        self.main_layout.addLayout(self.switch_name_layout)

        # タイプ
        self.switch_type_layout = QtWidgets.QHBoxLayout()
        self.switch_type = QtWidgets.QLabel("", self)
        self.switch_type.setAlignment(Qt.AlignCenter)
        self.switch_type_layout.addWidget(self.switch_type)
        self.main_layout.addLayout(self.switch_type_layout)

        # 押下圧
        self.force_layout = QtWidgets.QHBoxLayout()
        self.force = QtWidgets.QLabel("", self)
        self.force.setAlignment(Qt.AlignCenter)
        self.force_layout.addWidget(self.force)
        self.main_layout.addLayout(self.force_layout)

        # Link
        self.link_layout = QtWidgets.QHBoxLayout()
        self.link = QtWidgets.QLabel("", self)
        self.link.setOpenExternalLinks(True)
        self.link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.link.setAlignment(Qt.AlignCenter)
        self.link.setTextFormat(Qt.RichText)
        self.link_layout.addWidget(self.link)
        self.main_layout.addLayout(self.link_layout)

        # 編集ボタン
        self.edit_button = QtWidgets.QPushButton("Edit", self)
        self.edit_button.clicked.connect(self.open_settings)
        self.edit_button.hide()
        self.main_layout.addWidget(self.edit_button)

        self.setLayout(self.main_layout)

    def change_base_dir(self):
        options = QtWidgets.QFileDialog.Options()
        new_base_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", "",
                                                     options=options)
        if new_base_dir:
            print(f"{new_base_dir=}")
            self.settings.setValue("base_dir", new_base_dir)
            self.update_setting(new_base_dir)
            self.key_map = self.load_key_map()

    def update_setting(self, base_dir):
        self.base_dir = base_dir
        self.config_file = os.path.join(self.base_dir, "key_map.json")
        self.image_dir = os.path.join(self.base_dir, "images")
        os.makedirs(self.image_dir, exist_ok=True)

    def load_key_map(self):
        if not os.path.exists(self.config_file):
            with open(self.config_file, "w") as file:
                json.dump(DEFAULT_INFO, file, indent=4)
        with open(self.config_file, "r") as file:
            return json.load(file)

    def keyPressEvent(self, event):
        key = event.text().lower()
        if key != "" and key in QWERT_KEYS:
            self.key = key
            self.message_label.hide()
            self.display_info()
            self.edit_button.show()

    def display_info(self):
        # キーの表示
        self.key_label.setText(f"Key: {self.key}")

        if self.key in self.key_map:
            key_info = self.key_map[self.key]

            # 画像の表示
            if key_info["image"]:
                pixmap = QtGui.QPixmap(key_info["image"])
                scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.clear()

            # 詳細の表示
            self.switch_name.setText(f'Name: {key_info["switch_name"]}')
            self.switch_type.setText(f'Type: {key_info["switch_type"]}')
            self.force.setText(f'Operation Force: {key_info["operation_force"]}')
            self.link.setText('<a href="{}">link</a>'.format(key_info["link"]))
        else:
            self.message_label.setText("No information available.")
            self.message_label.show()
            self.image_label.clear()
            self.switch_name.clear()
            self.switch_type.clear()
            self.force.clear()
            self.link.clear()

    def open_settings(self):
        if self.key not in self.key_map:
            self.key_map[self.key] = self.key_map["default"]

        settings_window = QtWidgets.QDialog(self)
        settings_window.setWindowTitle("Settings")
        main_layout = QtWidgets.QVBoxLayout()

        # キー
        key_layout = QtWidgets.QHBoxLayout()
        key_label = QtWidgets.QLabel(f"Key: {self.key}")
        key_layout.addWidget(key_label)
        main_layout.addLayout(key_layout)

        # 画像
        self.is_image_updated = False
        image_layout = QtWidgets.QHBoxLayout()
        image_label = QtWidgets.QLabel("Image: ")
        image_layout.addWidget(image_label)

        image = QtWidgets.QLabel(os.path.basename(self.key_map[self.key]["image"]))
        image_layout.addWidget(image)

        choose_image_button = QtWidgets.QPushButton("Choose Image", self)
        choose_image_button.clicked.connect(lambda: self.choose_image(image))
        image_layout.addWidget(choose_image_button)
        main_layout.addLayout(image_layout)

        # 名前
        name_layout = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("Name: ")
        name_layout.addWidget(name_label)

        name_entry = QtWidgets.QLineEdit(self)
        name_entry.setText(self.key_map[self.key]["switch_name"])
        name_layout.addWidget(name_entry)
        main_layout.addLayout(name_layout)

        # タイプ
        type_layout = QtWidgets.QHBoxLayout()
        type_label = QtWidgets.QLabel("Type: ")
        type_layout.addWidget(type_label)

        type_entry = QtWidgets.QComboBox()
        type_entry.addItems(SWITCH_TYPES)
        type_entry.setCurrentText(self.key_map[self.key]["switch_type"])
        type_layout.addWidget(type_entry)
        main_layout.addLayout(type_layout)

        # 押下圧
        force_layout = QtWidgets.QHBoxLayout()
        force_label = QtWidgets.QLabel("Operation Force: ")
        force_layout.addWidget(force_label)

        force_entry = QtWidgets.QLineEdit(self)
        force_entry.setText(self.key_map[self.key]["operation_force"])
        force_layout.addWidget(force_entry)
        main_layout.addLayout(force_layout)

        # Link
        link_layout = QtWidgets.QHBoxLayout()
        link_label = QtWidgets.QLabel("Link URL:  ")
        link_layout.addWidget(link_label)

        link_entry = QtWidgets.QLineEdit(self)
        link_entry.setText(self.key_map[self.key]["link"])
        link_layout.addWidget(link_entry)
        main_layout.addLayout(link_layout)

        # Saveボタン
        save_button = QtWidgets.QPushButton("Save", self)
        entry_map = {
            "image": image,
            "switch_name": name_entry,
            "switch_type": type_entry,
            "operation_force": force_entry,
            "link": link_entry
        }
        save_button.clicked.connect(lambda: self.update_key_map(entry_map, settings_window))
        main_layout.addWidget(save_button)

        # Deleteボタン
        delete_button = QtWidgets.QPushButton("Delete", self)
        delete_button.clicked.connect(lambda: self.clear_key_info(settings_window))
        main_layout.addWidget(delete_button)

        settings_window.setLayout(main_layout)
        settings_window.exec_()

    def choose_image(self, image):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Image", "",
                                                             "Images (*.png *.jpg *.jpeg)")
        image.setText(file_path)
        self.is_image_updated = True

    def update_key_map(self, entry_map, settings_window):
        self.save_image(entry_map["image"])
        self.key_map[self.key]["switch_name"] = entry_map["switch_name"].text()
        self.key_map[self.key]["switch_type"] = entry_map["switch_type"].currentText()
        self.key_map[self.key]["operation_force"] = entry_map["operation_force"].text()
        self.key_map[self.key]["link"] = entry_map["link"].text()
        self.save_key_map()
        self.display_info()
        self.message_label.hide()
        settings_window.close()

    def save_image(self, image):
        file_path = image.text()
        if file_path and self.is_image_updated:
            saved_path = os.path.join(self.image_dir, os.path.basename(file_path))
            shutil.copy(file_path, saved_path)
            self.key_map[self.key]["image"] = saved_path

    def save_key_map(self):
        with open(self.config_file, "w") as file:
            json.dump(self.key_map, file, indent=4)

    def clear_key_info(self, settings_window):
        self.key_map.pop(self.key)
        self.save_key_map()
        self.display_info()
        settings_window.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = KeyTesterApp()
    window.show()
    sys.exit(app.exec_())