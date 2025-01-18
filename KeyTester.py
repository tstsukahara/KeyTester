"""KeyTesterアプリ"""

import shutil
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
import json
import os

from PyQt5.QtGui import QKeyEvent

from constants import DEFAULT_BASE_DIR, CONF_FILE, IMAGE_DIR, VALID_KEYS, DEFAULT_INFO, SWITCH_TYPES


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

    def init_ui(self):
        """UI初期化メソッド"""
        # メニューバーの作成
        menubar = self.menuBar()
        setting_menu = menubar.addMenu("Settings")
        change_base_dir_action = QtWidgets.QAction("Change Base Directory", self)
        change_base_dir_action.triggered.connect(self.change_base_dir)
        setting_menu.addAction(change_base_dir_action)

        # メインレイアウト
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(central_widget)

        # ラベル作成
        self.key_label = self.create_label("", Qt.AlignCenter)
        self.message_label = self.create_label("Press any key.", Qt.AlignCenter)
        self.image_label = self.create_label("", Qt.AlignCenter)
        self.switch_name_label = self.create_label("", Qt.AlignCenter, bold=True, font_size=20)
        self.switch_type_label = self.create_label("", Qt.AlignCenter)
        self.top_housing_label = self.create_label("", Qt.AlignCenter)
        self.bottom_housing_label = self.create_label("", Qt.AlignCenter)
        self.force_label = self.create_label("", Qt.AlignCenter)
        self.link_label = self.create_label("", Qt.AlignCenter, link=True)

        self.is_image_updated = False

        # 編集ボタン
        self.edit_button = QtWidgets.QPushButton("Edit", self)
        self.edit_button.clicked.connect(self.open_edit)
        self.edit_button.hide()

        # レイアウト構築
        for widget in [
            self.key_label,
            self.message_label,
            self.image_label,
            self.switch_name_label,
            self.switch_type_label,
            self.top_housing_label,
            self.bottom_housing_label,
            self.force_label,
            self.link_label,
            self.edit_button,
        ]:
            self.main_layout.addWidget(widget)

        self.setLayout(self.main_layout)

    def change_base_dir(self):
        """ベースディレクトリを変更する"""
        new_base_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if new_base_dir:
            self.settings.setValue("base_dir", new_base_dir)
            self.update_setting(new_base_dir)
            self.key_map = self.load_key_map()

    def update_setting(self, base_dir: str) -> None:
        """設定の更新"""
        self.base_dir = base_dir
        self.config_file = os.path.join(self.base_dir, "key_map.json")
        self.image_dir = os.path.join(self.base_dir, "images")
        os.makedirs(self.image_dir, exist_ok=True)

    def create_label(self, text, alignment, bold=False, font_size=None, link=False):
        """ラベル生成ヘルパー"""
        label = QtWidgets.QLabel(text, self)
        label.setAlignment(alignment)

        if bold or font_size:
            style = ""
            if bold:
                style += "font-weight: bold;"
            if font_size:
                style += f"font-size: {font_size}px;"
            label.setStyleSheet(style)

        if link:
            label.setOpenExternalLinks(True)
            label.setTextInteractionFlags(Qt.TextBrowserInteraction)
            label.setTextFormat(Qt.RichText)

        return label

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """キー押下時のイベント"""
        key = event.text().lower()
        if key != "" and key in VALID_KEYS:
            self.key = key
            self.message_label.hide()
            self.update_display_info()
            self.edit_button.show()

    def update_display_info(self):
        """表示する情報を更新する"""
        self.key_label.setText(f"Key: {self.key}")
        key_info = self.key_map.get(self.key, None)

        if key_info:
            self.update_label(self.image_label, key_info.get("image"), is_image=True)
            self.update_label(self.switch_name_label, key_info.get("switch_name"))
            self.update_label(self.switch_type_label, f"Type: {key_info.get('switch_type')}")
            self.update_label(self.top_housing_label, f"Top Housing: {key_info.get('top_housing')}")
            self.update_label(self.bottom_housing_label, f"Bottom Housing: {key_info.get('bottom_housing')}")
            self.update_label(self.force_label, f"Operation Force: {key_info.get('operation_force')}")
            self.update_label(self.link_label, 'Link: <a href="{}">url</a>'.format(key_info.get("link")))
        else:
            self.clear_info()



    def update_label(self, label, content, is_image=False):
        """ラベルの更新"""
        if is_image:
            pixmap = QtGui.QPixmap(content)
            label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        else:
            label.setText(content or "")

    def clear_info(self):
        """キースイッチ情報のクリア"""
        self.message_label.setText("No information available.")
        self.message_label.show()
        for label in [
            self.image_label,
            self.switch_name_label,
            self.switch_type_label,
            self.top_housing_label,
            self.bottom_housing_label,
            self.force_label,
            self.link_label
        ]:
            label.clear()

    def load_key_map(self) -> dict[str, str]:
        """key_mapを読み込む"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                return json.load(file)
        else:
            return {}

    def open_edit(self):
        """編集ダイアログを開く"""
        if self.key not in self.key_map:
            self.key_map[self.key] = DEFAULT_INFO

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Edit Switch Information")
        dialog_main_layout = QtWidgets.QVBoxLayout()

        # キー
        key_layout = QtWidgets.QHBoxLayout()
        key_label = QtWidgets.QLabel(f"Key: {self.key}")
        key_layout.addWidget(key_label)

        # 画像
        self.is_image_updated = False
        image_layout = QtWidgets.QHBoxLayout()
        image_label = QtWidgets.QLabel("Image: ")
        image_layout.addWidget(image_label)
        image_path = QtWidgets.QLabel(os.path.basename(self.key_map[self.key]["image"]))
        image_layout.addWidget(image_path)
        choose_image_button = QtWidgets.QPushButton("Choose Image", self)
        choose_image_button.clicked.connect(lambda: self.choose_image(image_path))
        image_layout.addWidget(choose_image_button)

        # スイッチ名
        name_layout = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("Name: ")
        name_layout.addWidget(name_label)
        name_input = QtWidgets.QLineEdit(self)
        name_input.setText(self.key_map[self.key]["switch_name"])
        name_layout.addWidget(name_input)

        # スイッチタイプ
        type_layout = QtWidgets.QHBoxLayout()
        type_label = QtWidgets.QLabel("Type: ")
        type_layout.addWidget(type_label)
        type_combo = QtWidgets.QComboBox()
        type_combo.addItems(SWITCH_TYPES)
        type_combo.setCurrentText(self.key_map.get(self.key).get("switch_type"))
        type_layout.addWidget(type_combo)

        # トップハウジング
        top_housing_layout = QtWidgets.QHBoxLayout()
        top_housing_label = QtWidgets.QLabel("Top Housing: ")
        top_housing_layout.addWidget(top_housing_label)
        top_housing_input = QtWidgets.QLineEdit(self)
        top_housing_input.setText(self.key_map.get(self.key).get("top_housing"))
        top_housing_layout.addWidget(top_housing_input)

        # ボトムハウジング
        bottom_housing_layout = QtWidgets.QHBoxLayout()
        bottom_housing_label = QtWidgets.QLabel("Bottom Housing: ")
        bottom_housing_layout.addWidget(bottom_housing_label)
        bottom_housing_input = QtWidgets.QLineEdit(self)
        bottom_housing_input.setText(self.key_map.get(self.key).get("bottom_housing"))
        bottom_housing_layout.addWidget(bottom_housing_input)

        # 押下圧
        force_layout = QtWidgets.QHBoxLayout()
        force_label = QtWidgets.QLabel("Operation Force: ")
        force_layout.addWidget(force_label)
        force_input = QtWidgets.QLineEdit(self)
        force_input.setText(self.key_map.get(self.key).get("operation_force"))
        force_layout.addWidget(force_input)

        # Link
        link_layout = QtWidgets.QHBoxLayout()
        link_label = QtWidgets.QLabel("Link URL:  ")
        link_layout.addWidget(link_label)
        link_input = QtWidgets.QLineEdit(self)
        link_input.setText(self.key_map.get(self.key).get("link"))
        link_layout.addWidget(link_input)

        # Saveボタン
        save_button = QtWidgets.QPushButton("Save", self)
        entry_map = {
            "image": image_path,
            "switch_name": name_input,
            "switch_type": type_combo,
            "top_housing": top_housing_input,
            "bottom_housing": bottom_housing_input,
            "operation_force": force_input,
            "link": link_input,
        }
        save_button.clicked.connect(
            lambda: self.update_key_map(entry_map, dialog)
        )

        # Deleteボタン
        delete_button = QtWidgets.QPushButton("Delete", self)
        delete_button.clicked.connect(lambda: self.delete_key_info(dialog))

        # レイアウト構築
        for layout in [
            key_layout,
            image_layout,
            name_layout,
            type_layout,
            top_housing_layout,
            bottom_housing_layout,
            force_layout,
            link_layout
        ]:
            dialog_main_layout.addLayout(layout)

        for widget in [
            save_button,
            delete_button
        ]:
            dialog_main_layout.addWidget(widget)

        dialog.setLayout(dialog_main_layout)
        dialog.exec_()

    def choose_image(self, image_path):
        """画像を選択する"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Image", "", f"Images (*.png, *.jpg *.jpeg)"
        )
        if file_path:
            image_path.setText(file_path)
            self.is_image_updated = True

    def update_key_map(self, entry_map, settings_window):
        """情報を更新する"""
        self.save_image(entry_map["image"])
        self.key_map[self.key]["switch_name"] = entry_map["switch_name"].text()
        self.key_map[self.key]["switch_type"] = entry_map["switch_type"].currentText()
        self.key_map[self.key]["top_housing"] = entry_map["top_housing"].text()
        self.key_map[self.key]["bottom_housing"] = entry_map["bottom_housing"].text()
        self.key_map[self.key]["operation_force"] = entry_map["operation_force"].text()
        self.key_map[self.key]["link"] = entry_map["link"].text()
        self.save_key_map()
        self.update_display_info()
        self.message_label.hide()
        settings_window.close()

    def save_image(self, image):
        """画像を保存する"""
        file_path = image.text()
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
