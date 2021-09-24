import json
from typing import Dict

default_locale = "en-gb"
cached_strings: Dict = {}


def refresh():
    global cached_strings
    with open(f"strings/{default_locale}.json") as f:
        cached_strings = json.load(f)


def getText(name):
    return cached_strings[name]


refresh()

