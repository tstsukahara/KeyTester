from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
import sys
import json
import os
import shutil

class KeyTesterApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Key Switch Tester")
        self.setGeometry(100, 100, 400, 400)

        # キーマッピングの保存ファイル
        self.config_file = "key_map.json"
        self.image_dir = "images"
        os.makedirs(self.image_dir, exist_ok=True)
        self.key_map = self.load_key_map()

        # レイアウトの作成
        self.layout = QtWidgets.QVBoxLayout()

        self.info_label = QtWidgets.QLabel("Press any key", self)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-size: 16px;")
        self.layout.addWidget(self.info_label)

        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.description_label = QtWidgets.QLabel("", self)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.description_label)

        self.settings_button = QtWidgets.QPushButton("Settings", self)
        self.settings_button.clicked.connect(self.open_settings)
        self.layout.addWidget(self.settings_button)

        self.setLayout(self.layout)

    def load_key_map(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                return json.load(file)
        else:
            return {
                "a": {"image": None, "description": "Cherry MX Red"},
                "b": {"image": None, "description": "Cherry MX Blue"},
            }

    def save_key_map(self):
        with open(self.config_file, "w") as file:
            json.dump(self.key_map, file, indent=4)

    def keyPressEvent(self, event):
        key = event.text().lower()
        if key in self.key_map:
            key_info = self.key_map[key]

            # 画像の表示
            if key_info["image"]:
                pixmap = QtGui.QPixmap(key_info["image"])
                scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.clear()

            # 説明の表示
            self.description_label.setText(key_info["description"])
        else:
            self.image_label.clear()
            self.description_label.setText("No information available")

    def open_settings(self):
        settings_window = QtWidgets.QDialog(self)
        settings_window.setWindowTitle("Settings")
        settings_layout = QtWidgets.QVBoxLayout()

        for key, info in self.key_map.items():
            key_label = QtWidgets.QLabel(f"Key: {key}")
            settings_layout.addWidget(key_label)

            description_entry = QtWidgets.QLineEdit(self)
            description_entry.setText(info["description"])
            settings_layout.addWidget(description_entry)

            choose_image_button = QtWidgets.QPushButton("Choose Image", self)
            settings_layout.addWidget(choose_image_button)

            def choose_image(key=key):
                file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
                if file_path:
                    # Save the selected image with a fixed file name based on the key
                    saved_path = os.path.join(self.image_dir, f"{key}.png")
                    shutil.copy(file_path, saved_path)
                    self.key_map[key]["image"] = saved_path

            choose_image_button.clicked.connect(lambda _, key=key: choose_image(key))

            def update_info(key=key, entry=description_entry):
                self.key_map[key]["description"] = entry.text()

            save_button = QtWidgets.QPushButton("Save", self)
            save_button.clicked.connect(lambda _, key=key, entry=description_entry: update_info(key, entry))
            settings_layout.addWidget(save_button)

        save_all_button = QtWidgets.QPushButton("Save All", self)
        save_all_button.clicked.connect(self.save_key_map)
        settings_layout.addWidget(save_all_button)

        settings_window.setLayout(settings_layout)
        settings_window.exec_()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = KeyTesterApp()
    window.show()
    sys.exit(app.exec_())
