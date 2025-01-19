import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QInputDialog

from constants import SWITCH_TYPES, FIELDS, DEFAULT_INFO


class EditSwitchDialog(QtWidgets.QDialog):
    def __init__(self, parent, key):
        super().__init__(parent)
        self.parent = parent
        self.key = key
        self.switch_info = self.parent.switch_info_manager.get_switch_info()
        self.switch_names = list(self.switch_info.keys())
        self.current_switch_name = list(self.switch_info.keys())[0]
        self.last_opened_directory = os.path.join(os.environ["HOME"], "Downloads")
        self.labels = {}
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Edit Switch Information")
        self.setGeometry(600, 300, 400, 400)
        self.layout = QtWidgets.QVBoxLayout(self)

        # スイッチ名
        self.switch_name_combo = QtWidgets.QComboBox()
        self.switch_name_combo.addItems(self.switch_names)
        self.switch_name_combo.setCurrentText(self.current_switch_name)
        self.switch_name_combo.currentIndexChanged.connect(self._on_switch_name_changed)
        self.layout.addLayout(self._create_combo_layout("Switch Name: ", self.switch_name_combo))

        # 画像
        self.image_path = QtWidgets.QLabel(os.path.basename(self.switch_info.get(self.current_switch_name).get("image")))
        self.layout.addLayout(self._create_image_layout())

        # スイッチタイプ
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(SWITCH_TYPES)
        self.type_combo.setCurrentText(self.switch_info.get(self.current_switch_name).get("switch_type"))
        # self.layout.addLayout(self._create_combo_layout("Type: ", self.type_combo))

        # その他フィールド
        self.fields = {}
        exclude_fields = ["switch_name", "image", "switch_type"]
        for field in filter(lambda f: f not in exclude_fields, FIELDS):
            self.fields[field], field_layout = self._create_layout_with_input(
                f"{field.replace('_', ' ').title()}: ", self.switch_info.get(self.current_switch_name).get(field, "")
            )
            self.layout.addLayout(field_layout)

        # 区切り線
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.layout.addWidget(line)

        # Saveボタン
        self.save_button = QtWidgets.QPushButton("Save", self)
        self.save_button.clicked.connect(self._save)
        self.layout.addWidget(self.save_button)

        # Deleteボタン
        self.delete_button = QtWidgets.QPushButton("Delete", self)
        self.delete_button.clicked.connect(self._show_confirm)
        self.layout.addWidget(self.delete_button)

        # Newボタン
        self.new_button = QtWidgets.QPushButton("Create New", self)
        self.new_button.clicked.connect(self._create_new)
        self.layout.addWidget(self.new_button)

        # Cancelボタン
        self.cancel_button = QtWidgets.QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self._cancel)
        self.layout.addWidget(self.cancel_button)
        self.cancel_button.hide()

        # Closeボタン
        self.close_button = QtWidgets.QPushButton("Close", self)
        self.close_button.clicked.connect(self._close)
        self.layout.addWidget(self.close_button)



    def _create_new(self):
        # 新しいスイッチ名の入力を求める
        new_name, ok = QInputDialog.getText(self, 'New Switch', 'Enter new switch name:')
        if ok and new_name:
            if new_name in self.switch_names:
                QMessageBox.warning(self, "Warning", "This switch name already exists.")
                return
            # 新しいスイッチ情報を初期化
            self.switch_info[new_name] = DEFAULT_INFO
            self.switch_info[new_name]["switch_name"] = new_name
            self.switch_names.append(new_name)
            self.current_switch_name = new_name
            self.switch_name_combo.addItem(new_name)
            self.switch_name_combo.setCurrentText(new_name)
            # フィールドをクリア
            self.image_path.setText("")
            self.type_combo.setCurrentIndex(0)
            for field, widget in self.fields.items():
                widget.setText("")

            self.switch_name_combo.setDisabled(True)
            self.delete_button.hide()
            self.new_button.hide()
            self.close_button.hide()
            self.cancel_button.show()

    def _on_switch_name_changed(self, index):
        self.current_switch_name = self.switch_names[index]
        self._update_display()

    def _update_display(self):
        # 画像の更新
        self.image_path.setText(os.path.basename(self.switch_info.get(self.current_switch_name).get("image")))
        # スイッチタイプの更新
        self.type_combo.setCurrentText(self.switch_info.get(self.current_switch_name).get("switch_type"))
        # その他フィールドの更新
        for field, widget in self.fields.items():
            widget.setText(self.switch_info.get(self.current_switch_name).get(field, ""))

    def _show_confirm(self):
        # 確認ダイアログの表示
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to delete switch info?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._delete()

    def _choose_image(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Image", self.last_opened_directory, "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.last_opened_directory = '/'.join(file_path.split('/')[:-1])
            self.image_path.setText(file_path)

    def _save(self):
        for field, widget in self.fields.items():
            if isinstance(widget, QtWidgets.QComboBox):
                self.switch_info.get(self.current_switch_name)[field] = widget.currentText()
            else:
                self.switch_info.get(self.current_switch_name)[field] = widget.text()

        new_image_path = self.parent.key_info_manager.save_image(self.image_path.text())
        if new_image_path:
            self.switch_info.get(self.current_switch_name)["image"] = os.path.basename(new_image_path)

        self.parent.switch_info_manager.update_switch_info(self.current_switch_name, self.switch_info.get(self.current_switch_name))
        self.parent.ui_manager.update_display_info(self.key, self.switch_info.get(self.current_switch_name))

        self.switch_name_combo.setDisabled(False)
        self.delete_button.show()
        self.close_button.show()
        self.new_button.show()
        self.cancel_button.hide()

    def _delete(self):
        self.parent.switch_info_manager.delete_switch_info(self.current_switch_name)
        self.switch_names.remove(self.current_switch_name)
        self.switch_name_combo.removeItem(self.switch_name_combo.findText(self.current_switch_name))
        self.parent.ui_manager.update_display_info(self.key, None)

    def _cancel(self):
        self.switch_names.remove(self.current_switch_name)
        self.parent.switch_info_manager.delete_switch_info(self.current_switch_name)
        self.switch_name_combo.removeItem(self.switch_name_combo.findText(self.current_switch_name))
        self.switch_name_combo.setCurrentText(self.current_switch_name)

        self.switch_name_combo.setDisabled(False)
        self.delete_button.show()
        self.close_button.show()
        self.new_button.show()
        self.cancel_button.hide()

    def _close(self):
        self.current_switch_name = self.switch_names[0]
        self.switch_name_combo.setCurrentText(self.current_switch_name)
        self.accept()

    def _create_image_layout(self):
        """画像レイアウト作成ヘルパー"""
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Image: "))
        layout.addWidget(self.image_path)
        choose_image_button = QtWidgets.QPushButton("Choose Image", self)
        choose_image_button.clicked.connect(self._choose_image)
        layout.addWidget(choose_image_button)
        return layout

    def _create_combo_layout(self, label_text, combo):
        """comboレイアウト作成ヘルパー"""
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel(label_text))
        layout.addWidget(combo)
        return layout

    def _create_layout_with_input(self, label_text, input_text):
        """labelとinputを含むレイアウト作成ヘルパー"""
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel(label_text))
        input_field = QtWidgets.QLineEdit(self)
        input_field.setText(input_text)
        layout.addWidget(input_field)
        return input_field, layout
