# options.py
import os

# --- Helper for environment overrides ---

def _env_or_default(env_key: str, default):
    """
    Return the value of environment variable `env_key` if set, else `default`.
    """
    return os.environ.get(env_key, default)

RUN_AS_STANDALONE_PYTHON = False

# --- Directory settings (override via ENV) ---
CBZ_DIR       = _env_or_default("CBZ_DIR",       "archives")
DOWNLOAD_DIR  = _env_or_default("DOWNLOAD_DIR",  "downloads")
DATA_DIR      = _env_or_default("DATA_DIR",      "data")
CONFIG_DIR    = _env_or_default("CONFIG_DIR",    "config")
LOG_DIR       = _env_or_default("LOG_DIR",       "logs")

# --- File names (override via ENV) ---
FAVORITES_FILE = _env_or_default("FAVORITES_FILE", "favorites.json")
METADATA_FILE  = _env_or_default("METADATA_FILE",  "metadata.json")
URL_FILE       = _env_or_default("URL_FILE",       "urls.json")
IDS_FILE       = _env_or_default("IDS_FILE",       "id_list.json")
CBZ_LIB_FILE   = _env_or_default("CBZ_LIB_FILE",   "cbzs.json")
SETTINGS_FILE  = _env_or_default("SETTINGS_FILE",  "settings.json")
SESSION_FILE   = _env_or_default("SESSION_FILE",   "session.json")

# --- Logging levels (override via ENV) ---
LOG_LVL         = _env_or_default("LOG_LVL",         "DEBUG")
LOG_CONSOLE_LVL = _env_or_default("LOG_CONSOLE_LVL", "DEBUG")
LOG_FILE_LVL    = _env_or_default("LOG_FILE_LVL",    "DEBUG")

# --- Default UI State (static) ---
DEFAULT_STATE = {
    "progress": {
        "favorites":  {"current": '--', "total": False},
        "errors":     {"current": 0,    "total": 100},
        "total":      {"current": '--', "total": '--'},
        "doujin":     {"current": '--', "total": '--'},
        "urls":       {"current": '--', "total": '--'},
        "downloads":  {"current": '--', "total": '--'},
        "conversion": {"current": '--', "total": '--'}
    },
    "control": {
        "mode":         'custom',
        "id_source":    'pre_fetched_favs',
        "run_until":    'urls',
        "start_button": 'start'
    },
    "settings": {
        "convert_to_webp":         True,
        "deleter_after_archiving": True,
        "save_live_progress":      True,
        "webp_quality":            None,
        "cbz_quality":             None,
        "max_retries":             10
    },
    "doujin_info": {
        "id":     "---",
        "title":  "---",
        "author": "---",
        "tags":   "---"
    },
    "show_cover":    False,
    "doujin_cover":  False,
    "task_running":  False
}

# --- Explanation ---
# 1) Each setting can be overridden by setting the corresponding environment variable.
#    Example: export DOWNLOAD_DIR="/data/downloads"
# 2) In your code, import from options.py, e.g.: 
#       from options import DOWNLOAD_DIR, DATA_DIR
# 3) Environment variables are read at import time, so you must set them before starting the app.
# 4) For integer or boolean overrides, you can wrap _env_or_default calls with conversion, e.g.:
#       MAX_RETRIES = int(_env_or_default("MAX_RETRIES", 10))
#       ENABLE_FEATURE = _env_or_default("ENABLE_FEATURE", "False").lower() in ("1","true","yes")
