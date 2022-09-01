# Leah
# strings.py
# Written by aquova et al., 2022
# https://github.com/StardewValleyDiscord/leah

import json

STRINGS_PATH = "./assets/strings.json"
with open(file=STRINGS_PATH, mode="r", encoding="utf8") as strings_file:
    _data = json.load(strings_file)

def get(__name: str):
    return _data.get(__name)
