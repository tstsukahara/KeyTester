import os

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

class UIManager:
    def __init__(self, parent):
        self.parent = parent
        self.labels = {}
        self.edit_button = None
        self.main_layout = None

    def setup_ui(self):
        self._setup_menu()
        self._setup_main_layout()
        self._setup_labels()
        self._setup_edit_button()

    def _setup_menu(self):
        menubar = self.parent.menuBar()
        setting_menu = menubar.addMenu("Settings")
        change_base_dir_action = QtWidgets.QAction("Change Base Directory", self.parent)
        change_base_dir_action.triggered.connect(self.parent.config_manager.change_base_dir)
        setting_menu.addAction(change_base_dir_action)

    def _setup_main_layout(self):
        central_widget = QtWidgets.QWidget()
        self.parent.setCentralWidget(central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(central_widget)

    def _setup_labels(self):
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
        for key, config in label_configs.items():
            self.labels[key] = self._create_label(**config)
            self.main_layout.addWidget(self.labels[key])

    def _setup_edit_button(self):
        self.edit_button = QtWidgets.QPushButton("Edit", self.parent)
        self.edit_button.clicked.connect(self.parent.open_edit)
        self.edit_button.hide()
        self.main_layout.addWidget(self.edit_button)

    def _create_label(self, text, alignment=Qt.AlignCenter, bold=False, font_size=None, link=False):
        label = QtWidgets.QLabel(text, self.parent)
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

    def update_display_info(self, key, key_info):
        self.labels["key"].setText(f"Key: {key}")
        if key_info:
            self._update_label_info(key_info)
        else:
            self._clear_labels()

    def _update_label_info(self, key_info):
        self._update_label(self.labels["image"], key_info.get("image"), is_image=True)
        for field in ["switch_name", "switch_type", "top_housing", "bottom_housing", "pin", "pre_travel",
                      "total_travel", "operation_force"]:
            field_title = f"{field.replace('_', ' ').title()}: " if field != "switch_name" else ''
            self._update_label(self.labels[field], f"{field_title}{key_info.get(field)}")
        self._update_label(self.labels["link"], f'Link: <a href="{key_info.get("link")}">url</a>')

    def _update_label(self, label, content, is_image=False):
        if is_image:
            label.clear()
            if os.path.exists(content):
                pixmap = QtGui.QPixmap(content)
                if not pixmap.isNull():
                    label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        else:
            label.setText(content or "")

    def _clear_labels(self):
        self.labels["message"].setText("No information available.")
        self.labels["message"].show()
        for label in self.labels.values():
            if label != self.labels["message"]:
                label.clear()

    def hide_label(self, label_name):
        self.labels[label_name].hide()

    def show_edit_button(self):
        self.edit_button.show()