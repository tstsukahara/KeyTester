"""定数の定義"""
import os

DEFAULT_BASE_DIR = os.path.join(os.environ["HOME"], "Documents/KeyTester")
CONF_FILE = "key_map.json"
IMAGE_DIR = "images"
VALID_KEYS = r"1234567890-=qwertyuiop[]\asdfghjkl;'zxcvbnm,./"
SWITCH_TYPES = ["-", "Linear", "Tactile", "Clicky", "Silent Linear", "Silent Tactile", "Silent Clicky",]
DEFAULT_INFO = {
    "image": "",
    "switch_name": "",
    "switch_type": "",
    "operation_force": "",
    "link": ""
}
