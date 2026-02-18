import os
import tomllib
import re

os.environ["SILENCE_TOKEN_WARNINGS"] = "true"

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_SCRIPT_DIR, "..", "config.toml")


HEX_COLOR_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def validate_hex_color(color: str) -> str:
    if not isinstance(color, str):
        raise TypeError("Hex color must be a string")

    if not HEX_COLOR_RE.match(color):
        raise ValueError(f"Invalid hex color: {color!r}")

    return color


with open(_CONFIG_PATH, "rb") as _f:
    _config = tomllib.load(_f)

STRAVA_CLIENT_ID: str = _config["strava"]["client_id"]
STRAVA_CLIENT_SECRET: str = _config["strava"]["client_secret"]
STRAVA_REFRESH_TOKEN: str = _config["strava"]["refresh_token"]

ACCENT_COLOR: str = validate_hex_color(_config["display"]["accent_color"])
DARK_MODE: bool = _config["display"]["dark_mode"]
FULL_SCREEN: bool = _config["display"]["full_screen"]
WIDTH: int = _config["display"]["width"]
HEIGHT: int = _config["display"]["height"]

REFRESH_TIME: int = _config["app"]["refresh_time_minutes"] * 60 * 1000

SLEEP_MODE_ENABLED: bool = _config["sleep_mode"]["enabled"]
SLEEP_MODE_START: int = _config["sleep_mode"]["start_hour"]
SLEEP_MODE_END: int = _config["sleep_mode"]["end_hour"]
