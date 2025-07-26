# Leah
# strings.py
# Written by aquova et al., 2022
# https://github.com/StardewValleyDiscord/leah

import os
from typing import Optional
import yaml

CURRENT_DIR = os.path.dirname(__file__)
ASSETS_PATH = os.path.join(CURRENT_DIR, "assets")
STRINGS_PATH = os.path.join(ASSETS_PATH, "strings.yaml")
with open(file=STRINGS_PATH, mode="r", encoding="utf8") as strings_file:
    _data = yaml.safe_load(strings_file)

emoji_success = "\N{WHITE HEAVY CHECK MARK}"
emoji_failure = "\N{CROSS MARK}"
emoji_redirect = "\N{RIGHTWARDS ARROW WITH HOOK}"

def get(__name: str) -> Optional[str]:
    return _data.get(__name)
