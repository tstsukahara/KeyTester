import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QInputDialog
from constants import SWITCH_TYPES, FIELDS, DEFAULT_INFO


class EditSwitchInfoDialog(QtWidgets.QDialog):
    def __init__(self, parent, key):
        super().__init__(parent)
        self.parent = parent
        self.key = key
        self.switch_info = self.parent.switch_info_manager.get_switch_info()
        self.switch_names = list(self.switch_info.keys())
        self.current_switch_name = self.switch_names[0]
        self.last_opened_directory = os.path.join(os.environ["HOME"], "Downloads")
        self.labels = {}
        self.fields = {}
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Edit Switch Information")
        self.setGeometry(600, 300, 400, 400)
        self.layout = QtWidgets.QVBoxLayout(self)

        self._create_switch_name_combo()
        self._create_image_section()
        self._create_type_combo()
        self._create_other_fields()
        self._create_buttons()

    def _create_switch_name_combo(self):
        self.switch_name_combo = QtWidgets.QComboBox()
        self.switch_name_combo.addItems(self.switch_names)
        self.switch_name_combo.setCurrentText(self.current_switch_name)
        self.switch_name_combo.currentIndexChanged.connect(self._on_switch_name_changed)
        self.layout.addLayout(self._create_combo_layout("Switch Name: ", self.switch_name_combo))

    def _create_image_section(self):
        self.image_path = QtWidgets.QLabel(os.path.basename(self.switch_info[self.current_switch_name]["image"]))
        self.layout.addLayout(self._create_image_layout())

    def _create_type_combo(self):
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(SWITCH_TYPES)
        self.type_combo.setCurrentText(self.switch_info[self.current_switch_name]["switch_type"])
        self.layout.addLayout(self._create_combo_layout("Switch Type: ", self.type_combo))

    def _create_other_fields(self):
        exclude_fields = ["switch_name", "image", "switch_type"]
        for field in filter(lambda f: f not in exclude_fields, FIELDS):
            self.fields[field], field_layout = self._create_layout_with_input(
                f"{field.replace('_', ' ').title()}: ", self.switch_info[self.current_switch_name].get(field, "")
            )
            self.layout.addLayout(field_layout)

    def _create_buttons(self):
        self.layout.addWidget(self._create_separator())

        buttons = [
            ("Save", self._save),
            ("Delete", self._show_confirm),
            ("Create New", self._create_new),
            ("Cancel", self._cancel),
            ("Close", self._close)
        ]

        for text, callback in buttons:
            button = QtWidgets.QPushButton(text, self)
            button.clicked.connect(callback)
            self.layout.addWidget(button)
            setattr(self, f"{text.lower().replace(' ', '_')}_button", button)

        self.cancel_button.hide()

    def _on_switch_name_changed(self, index):
        self.current_switch_name = self.switch_names[index]
        self._update_display()

    def _update_display(self):
        self.image_path.setText(os.path.basename(self.switch_info[self.current_switch_name]["image"]))
        self.type_combo.setCurrentText(self.switch_info[self.current_switch_name]["switch_type"])
        for field, widget in self.fields.items():
            widget.setText(self.switch_info[self.current_switch_name].get(field, ""))

    def _show_confirm(self):
        reply = QMessageBox.question(self, 'Message', "Are you sure to delete switch info?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._delete()

    def _choose_image(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Image", self.last_opened_directory, "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.last_opened_directory = os.path.dirname(file_path)
            self.image_path.setText(file_path)

    def _save(self):
        for field, widget in self.fields.items():
            self.switch_info[self.current_switch_name][field] = widget.text()

        new_image_path = self.parent.key_map_manager.save_image(self.image_path.text())
        if new_image_path:
            self.switch_info[self.current_switch_name]["image"] = os.path.basename(new_image_path)

        self.parent.switch_info_manager.update_switch_info(self.current_switch_name,
                                                           self.switch_info[self.current_switch_name])
        self.parent.ui_manager.update_display_info(self.key, self.switch_info[self.current_switch_name])

        self._toggle_ui_elements(True)

    def _delete(self):
        self.parent.switch_info_manager.delete_switch_info(self.current_switch_name)
        self.switch_names.remove(self.current_switch_name)
        self.switch_name_combo.removeItem(self.switch_name_combo.findText(self.current_switch_name))
        self.parent.ui_manager.update_display_info(self.key, None)

    def _create_new(self):
        new_name, ok = QInputDialog.getText(self, 'New Switch', 'Enter new switch name:')
        if ok and new_name:
            if new_name in self.switch_names:
                QMessageBox.warning(self, "Warning", "This switch name already exists.")
                return
            self.switch_info[new_name] = DEFAULT_INFO.copy()
            self.switch_info[new_name]["switch_name"] = new_name
            self.switch_names.append(new_name)
            self.current_switch_name = new_name
            self.switch_name_combo.addItem(new_name)
            self.switch_name_combo.setCurrentText(new_name)
            self._clear_fields()
            self._toggle_ui_elements(False)

    def _cancel(self):
        self.switch_names.remove(self.current_switch_name)
        self.parent.switch_info_manager.delete_switch_info(self.current_switch_name)
        self.switch_name_combo.removeItem(self.switch_name_combo.findText(self.current_switch_name))
        self.switch_name_combo.setCurrentText(self.switch_names[0])
        self._toggle_ui_elements(True)

    def _close(self):
        self.current_switch_name = self.switch_names[0]
        self.switch_name_combo.setCurrentText(self.current_switch_name)
        self.accept()

    def _create_image_layout(self):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Image: "))
        layout.addWidget(self.image_path)
        choose_image_button = QtWidgets.QPushButton("Choose Image", self)
        choose_image_button.clicked.connect(self._choose_image)
        layout.addWidget(choose_image_button)
        return layout

    def _create_combo_layout(self, label_text, combo):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel(label_text))
        layout.addWidget(combo)
        return layout

    def _create_layout_with_input(self, label_text, input_text):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel(label_text))
        input_field = QtWidgets.QLineEdit(self)
        input_field.setText(input_text)
        layout.addWidget(input_field)
        return input_field, layout

    def _create_separator(self):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        return line

    def _clear_fields(self):
        self.image_path.setText("")
        self.type_combo.setCurrentIndex(0)
        for field, widget in self.fields.items():
            widget.setText("")

    def _toggle_ui_elements(self, enabled):
        self.switch_name_combo.setDisabled(not enabled)
        self.delete_button.setVisible(enabled)
        self.close_button.setVisible(enabled)
        self.create_new_button.setVisible(enabled)
        self.cancel_button.setVisible(not enabled)
