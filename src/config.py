import os
import tomllib
import re
import sys

os.environ["SILENCE_TOKEN_WARNINGS"] = "true"

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_SCRIPT_DIR, "..", "config.toml")

HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

_DEFAULTS = {
    "display": {
        "accent_color": "#FC4C02",
        "dark_mode": False,
        "full_screen": False,
        "width": 320,
        "height": 240,
    },
    "app": {
        "refresh_time_minutes": 15,
    },
    "sleep_mode": {
        "enabled": False,
        "start_hour": 22,
        "end_hour": 8,
    },
}

_errors: list[str] = []
_warnings: list[str] = []


def _get(config: dict, section: str, key: str):
    value = config.get(section, {}).get(key)
    if value is None:
        default = _DEFAULTS.get(section, {}).get(key)
        _warnings.append(f"[{section}] '{key}' not set — using default: {default!r}")
        return default
    return value


def _require(config: dict, section: str, key: str):
    value = config.get(section, {}).get(key)
    if value is None:
        _errors.append(f"[{section}] '{key}' is required but missing from config.toml")
    return value


def _validate_hex_color(value: str, section: str, key: str) -> str:
    if not isinstance(value, str):
        _errors.append(
            f"[{section}] '{key}' must be a string, got {type(value).__name__}"
        )
        return _DEFAULTS[section][key]
    if not HEX_COLOR_RE.match(value):
        _errors.append(
            f"[{section}] '{key}' is not a valid hex color (e.g. '#FC4C02'): {value!r}"
        )
        return _DEFAULTS[section][key]
    return value


def _validate_bool(value, section: str, key: str) -> bool:
    if not isinstance(value, bool):
        _errors.append(f"[{section}] '{key}' must be true or false, got {value!r}")
        return _DEFAULTS[section][key]
    return value


def _validate_int(
    value, section: str, key: str, min_val: int = None, max_val: int = None
) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        _errors.append(f"[{section}] '{key}' must be an integer, got {value!r}")
        return _DEFAULTS[section][key]
    if min_val is not None and value < min_val:
        _errors.append(f"[{section}] '{key}' must be >= {min_val}, got {value}")
        return _DEFAULTS[section][key]
    if max_val is not None and value > max_val:
        _errors.append(f"[{section}] '{key}' must be <= {max_val}, got {value}")
        return _DEFAULTS[section][key]
    return value


def _validate_str(value, section: str, key: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _errors.append(f"[{section}] '{key}' must be a non-empty string")
        return None
    return value


try:
    with open(_CONFIG_PATH, "rb") as _f:
        _config = tomllib.load(_f)
except FileNotFoundError:
    print(f"ERROR: config.toml not found at {_CONFIG_PATH}", file=sys.stderr)
    sys.exit(1)
except tomllib.TOMLDecodeError as e:
    print(f"ERROR: config.toml is not valid TOML: {e}", file=sys.stderr)
    sys.exit(1)

_client_id = _require(_config, "strava", "client_id")
_client_secret = _require(_config, "strava", "client_secret")
_refresh_token = _require(_config, "strava", "refresh_token")

STRAVA_CLIENT_ID: str = _validate_str(_client_id, "strava", "client_id")
STRAVA_CLIENT_SECRET: str = _validate_str(_client_secret, "strava", "client_secret")
STRAVA_REFRESH_TOKEN: str = _validate_str(_refresh_token, "strava", "refresh_token")

ACCENT_COLOR: str = _validate_hex_color(
    _get(_config, "display", "accent_color"), "display", "accent_color"
)
DARK_MODE: bool = _validate_bool(
    _get(_config, "display", "dark_mode"), "display", "dark_mode"
)
FULL_SCREEN: bool = _validate_bool(
    _get(_config, "display", "full_screen"), "display", "full_screen"
)
WIDTH: int = _validate_int(
    _get(_config, "display", "width"),
    "display",
    "width",
    min_val=1,
)
HEIGHT: int = _validate_int(
    _get(_config, "display", "height"),
    "display",
    "height",
    min_val=1,
)

REFRESH_TIME: int = (
    _validate_int(
        _get(_config, "app", "refresh_time_minutes"),
        "app",
        "refresh_time_minutes",
        min_val=_DEFAULTS["app"]["refresh_time_minutes"],
        max_val=1440,
    )
    * 60
    * 1000
)

SLEEP_MODE_ENABLED: bool = _validate_bool(
    _get(_config, "sleep_mode", "enabled"), "sleep_mode", "enabled"
)

if SLEEP_MODE_ENABLED:
    SLEEP_MODE_START: int = _validate_int(
        _get(_config, "sleep_mode", "start_hour"),
        "sleep_mode",
        "start_hour",
        min_val=0,
        max_val=23,
    )
    SLEEP_MODE_END: int = _validate_int(
        _get(_config, "sleep_mode", "end_hour"),
        "sleep_mode",
        "end_hour",
        min_val=0,
        max_val=23,
    )
    if SLEEP_MODE_START == SLEEP_MODE_END:
        _errors.append(
            "[sleep_mode] 'start_hour' and 'end_hour' cannot be the same value"
        )
else:
    SLEEP_MODE_START: int = _DEFAULTS["sleep_mode"]["start_hour"]
    SLEEP_MODE_END: int = _DEFAULTS["sleep_mode"]["end_hour"]

if _warnings:
    print("Config warnings:", file=sys.stderr)
    for w in _warnings:
        print(f"  • {w}", file=sys.stderr)

if _errors:
    print("Config errors — cannot start:", file=sys.stderr)
    for e in _errors:
        print(f"  ✗ {e}", file=sys.stderr)
    sys.exit(1)
