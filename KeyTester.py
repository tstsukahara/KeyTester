"""KeyTesterアプリ"""

import shutil
import json
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent

from constants import (
    DEFAULT_BASE_DIR,
    CONF_FILE,
    IMAGE_DIR,
    VALID_KEYS,
    DEFAULT_INFO,
    SWITCH_TYPES,
)

class KeyTester(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KeyTester")
        self.setGeometry(300, 200, 400, 400)
        self.init_conf()
        self.init_ui()

    def init_conf(self):
        """設定初期化メソッド"""
        self.settings = QtCore.QSettings("KeyTester", "Settings")
        self.base_dir = self.settings.value("base_dir", DEFAULT_BASE_DIR)
        self.config_file = os.path.join(self.base_dir, CONF_FILE)
        self.image_dir = os.path.join(self.base_dir, IMAGE_DIR)
        os.makedirs(self.image_dir, exist_ok=True)
        self.key_map = self.load_key_map()
        self.key = None
        self.is_image_updated = False

    def init_ui(self):
        """UI初期化メソッド"""
        self.setup_menu()
        self.setup_main_layout()
        self.setup_labels()
        self.setup_edit_button()

    def setup_menu(self):
        """メニューバー作成"""
        menubar = self.menuBar()
        setting_menu = menubar.addMenu("Settings")
        change_base_dir_action = QtWidgets.QAction("Change Base Directory", self)
        change_base_dir_action.triggered.connect(self.change_base_dir)
        setting_menu.addAction(change_base_dir_action)

    def setup_main_layout(self):
        """メインレイアウト作成"""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(central_widget)

    def setup_labels(self):
        """ラベル作成"""
        label_configs = {
            "key": {"text": ""},
            "message": {"text": "Press any key."},
            "image": {"text": ""},
            "switch_name": {"text": "", "bold": True, "font_size": 20},
            "switch_type": {"text": ""},
            "top_housing": {"text": ""},
            "bottom_housing": {"text": ""},
            "pin": {"text": ""},
            "pre_travel": {"text": ""},
            "total_travel": {"text": ""},
            "operation_force": {"text": ""},
            "link": {"text": "", "link": True},
        }
        self.labels = {key: self.create_label(**config) for key, config in label_configs.items()}
        for label in self.labels.values():
            self.main_layout.addWidget(label)

    def setup_edit_button(self):
        """編集ボタン作成"""
        self.edit_button = QtWidgets.QPushButton("Edit", self)
        self.edit_button.clicked.connect(self.open_edit)
        self.edit_button.hide()
        self.main_layout.addWidget(self.edit_button)

    def create_label(self, text, alignment=Qt.AlignCenter, bold=False, font_size=None, link=False):
        """ラベル生成ヘルパー"""
        label = QtWidgets.QLabel(text, self)
        label.setAlignment(alignment)
        style = []
        if bold:
            style.append("font-weight: bold;")
        if font_size:
            style.append(f"font-size: {font_size}px;")
        if style:
            label.setStyleSheet("".join(style))
        if link:
            label.setOpenExternalLinks(True)
            label.setTextInteractionFlags(Qt.TextBrowserInteraction)
            label.setTextFormat(Qt.RichText)
        return label

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """キー押下時のイベント"""
        key = event.text().lower()
        if key in VALID_KEYS:
            self.key = key
            self.labels["message"].hide()
            self.update_display_info()
            self.edit_button.show()

    def update_display_info(self):
        """表示する情報を更新する"""
        self.labels["key"].setText(f"Key: {self.key}")
        key_info = self.key_map.get(self.key)
        if key_info:
            self.update_label_info(key_info)
        else:
            self.clear_info()

    def update_label_info(self, key_info):
        self.update_label(self.labels["image"], key_info.get("image"), is_image=True)
        for field in ["switch_name", "switch_type", "top_housing", "bottom_housing", "pin", "pre_travel", "total_travel", "operation_force"]:
            field_title = f"{field.replace('_', ' ').title()}: " if field != "switch_name" else ''
            self.update_label(self.labels[field], f"{field_title}{key_info.get(field)}")
        self.update_label(self.labels["link"], f'Link: <a href="{key_info.get("link")}">url</a>')

    def update_label(self, label, content, is_image=False):
        """ラベルの更新"""
        if is_image:
            label.clear()
            if os.path.exists(content):
                pixmap = QtGui.QPixmap(content)
                if not pixmap.isNull():
                    label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        else:
            label.setText(content or "")

    def clear_info(self):
        """キースイッチ情報のクリア"""
        self.labels["message"].setText("No information available.")
        self.labels["message"].show()
        for label in self.labels.values():
            if label != self.labels["message"]:
                label.clear()

    def load_key_map(self) -> dict[str, str]:
        """key_mapを読み込む"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                return json.load(file)
        return {}

    def open_edit(self):
        """編集ダイアログを開く"""
        if self.key not in self.key_map:
            self.key_map[self.key] = DEFAULT_INFO.copy()

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Edit Switch Information")
        dialog_main_layout = QtWidgets.QVBoxLayout()

        self.setup_edit_dialog(dialog, dialog_main_layout)
        dialog.setLayout(dialog_main_layout)
        dialog.exec_()

    def setup_edit_dialog(self, dialog, layout):
        key_info = self.key_map[self.key]
        # キー
        layout.addWidget(QtWidgets.QLabel(f"Key: {self.key}"))

        # 画像
        self.is_image_updated = False
        self.image_path = QtWidgets.QLabel(os.path.basename(key_info["image"]))
        layout.addLayout(self.create_image_layout())

        # スイッチタイプ
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(SWITCH_TYPES)
        self.type_combo.setCurrentText(key_info.get("switch_type"))
        layout.addLayout(self.create_combo_layout("Type: ", self.type_combo))

        # その他フィールド
        self.input_fields = {}
        for field in [
            "switch_name",
            "top_housing",
            "bottom_housing",
            "pin",
            "pre_travel",
            "total_travel",
            "operation_force",
            "link"
        ]:
            self.input_fields[field], field_layout = self.create_layout_with_input(
                f"{field.replace('_', ' ').title()}: ", key_info.get(field, "")
            )
            layout.addLayout(field_layout)

        # Saveボタン
        save_button = QtWidgets.QPushButton("Save", self)
        save_button.clicked.connect(lambda: self.update_key_map(dialog))
        layout.addWidget(save_button)

        # Deleteボタン
        delete_button = QtWidgets.QPushButton("Delete", self)
        delete_button.clicked.connect(lambda: self.delete_key_info(dialog))
        layout.addWidget(delete_button)

    def create_image_layout(self):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Image: "))
        layout.addWidget(self.image_path)
        choose_image_button = QtWidgets.QPushButton("Choose Image", self)
        choose_image_button.clicked.connect(lambda: self.choose_image(self.image_path))
        layout.addWidget(choose_image_button)
        return layout

    def create_layout_with_input(self, label_text, input_text):
        """labelとinputを含むレイアウト作成ヘルパー"""
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel(label_text))
        input_field = QtWidgets.QLineEdit(self)
        input_field.setText(input_text)
        layout.addWidget(input_field)
        return input_field, layout

    def create_combo_layout(self, label_text, combo):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel(label_text))
        layout.addWidget(combo)
        return layout

    def choose_image(self, image_path):
        """画像を選択する"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Image", "", f"Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            image_path.setText(file_path)
            self.is_image_updated = True

    def update_key_map(self, dialog):
        """情報を更新する"""
        self.save_image()
        for field, input_field in self.input_fields.items():
            self.key_map[self.key][field] = input_field.text()
        self.key_map[self.key]["switch_type"] = self.type_combo.currentText()
        self.save_key_map()
        self.update_display_info()
        self.labels["message"].hide()
        dialog.close()

    def save_image(self):
        """画像を保存する"""
        file_path = self.image_path.text()
        if file_path and self.is_image_updated:
            saved_path = os.path.join(self.image_dir, os.path.basename(file_path))
            shutil.copy(file_path, saved_path)
            self.key_map[self.key]["image"] = saved_path

    def save_key_map(self):
        """キーマップファイルを保存する"""
        with open(self.config_file, "w") as file:
            json.dump(self.key_map, file, indent=4)

    def delete_key_info(self, dialog):
        """キーマップを削除する"""
        self.key_map.pop(self.key)
        self.save_key_map()
        self.update_display_info()
        dialog.close()

    def change_base_dir(self):
        """ベースディレクトリを変更する"""
        new_base_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory"
        )
        if new_base_dir:
            self.settings.setValue("base_dir", new_base_dir)
            self.update_setting(new_base_dir)
            self.key_map = self.load_key_map()

    def update_setting(self, base_dir: str) -> None:
        """設定の更新"""
        self.base_dir = base_dir
        self.config_file = os.path.join(self.base_dir, CONF_FILE)
        self.image_dir = os.path.join(self.base_dir, IMAGE_DIR)
        os.makedirs(self.image_dir, exist_ok=True)