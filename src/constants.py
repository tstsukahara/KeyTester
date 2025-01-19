"""定数の定義"""
import os

DEFAULT_BASE_DIR = os.path.join(os.environ["HOME"], "Documents/KeyTester")
KEY_MAP_FILE = "key_map.json"
SWITCH_FILE = "switch.json"
IMAGE_DIR = "images"
VALID_KEYS = r"1234567890-=qwertyuiop[]\asdfghjkl;'zxcvbnm,./"
SWITCH_TYPES = ["-", "Linear", "Tactile", "Clicky", "Silent Linear", "Silent Tactile", "Silent Clicky",]
FIELDS = [
            "image",
            "switch_name",
            "switch_type",
            "top_housing",
            "bottom_housing",
            "pin",
            "pre_travel",
            "total_travel",
            "operation_force",
            "bottom_out_force",
            "spring",
            "factory_lubed",
            "price",
            "link",
]
DEFAULT_INFO = dict.fromkeys(FIELDS, "")
