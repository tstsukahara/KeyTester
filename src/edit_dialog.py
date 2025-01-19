import os

from PyQt5 import QtWidgets

from constants import SWITCH_TYPES, FIELDS


class EditDialog(QtWidgets.QDialog):
    def __init__(self, parent, key, key_info):
        super().__init__(parent)
        self.parent = parent
        self.key = key
        self.key_info = key_info.copy()
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Edit Switch Information")
        layout = QtWidgets.QVBoxLayout(self)

        # キー
        layout.addWidget(QtWidgets.QLabel(f"Key: {self.key}"))

        # 画像
        self.image_path = QtWidgets.QLabel(os.path.basename(self.key_info["image"]))
        layout.addLayout(self._create_image_layout())

        # スイッチタイプ
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(SWITCH_TYPES)
        self.type_combo.setCurrentText(self.key_info.get("switch_type"))
        layout.addLayout(self._create_combo_layout("Type: ", self.type_combo))

        # その他フィールド
        self.fields = {}
        exclude_fields = ["image", "switch_type"]
        for field in filter(lambda f: f not in exclude_fields, FIELDS):
            self.fields[field], field_layout = self._create_layout_with_input(
                f"{field.replace('_', ' ').title()}: ", self.key_info.get(field, "")
            )
            layout.addLayout(field_layout)

        # Saveボタン
        save_button = QtWidgets.QPushButton("Save", self)
        save_button.clicked.connect(self._save)
        layout.addWidget(save_button)

        # Deleteボタン
        delete_button = QtWidgets.QPushButton("Delete", self)
        delete_button.clicked.connect(self._delete)
        layout.addWidget(delete_button)

    def _choose_image(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.image_path.setText(file_path)

    def _save(self):
        for field, widget in self.fields.items():
            if isinstance(widget, QtWidgets.QComboBox):
                self.key_info[field] = widget.currentText()
            else:
                self.key_info[field] = widget.text()

        new_image_path = self.parent.key_info_manager.save_image(self.image_path.text())
        if new_image_path:
            self.key_info["image"] = os.path.basename(new_image_path)

        self.parent.key_info_manager.update_key_info(self.key, self.key_info)
        self.parent.ui_manager.update_display_info(self.key, self.key_info)
        self.accept()

    def _delete(self):
        self.parent.key_info_manager.delete_key_info(self.key)
        self.parent.ui_manager.update_display_info(self.key, None)
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