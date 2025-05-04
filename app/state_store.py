
import threading
import copy
import options

# In-memory state and lock for thread-safe access\ n_state = None
_state = None
_lock = threading.Lock()

if hasattr(options, 'DEFAULT_STATE'):
    _default_state = options.DEFAULT_STATE
else:
    _default_state = {
        "progress": {
            "favorites":    {"current": '--',  "total": False},
            "errors":       {"current": 0,  "total": 100},
            "total":        {"current": '--',  "total": '--'},
            "doujin":       {"current": '--',  "total": '--'},
            "urls":         {"current": '--',  "total": '--'},
            "downloads":    {"current": '--',  "total": '--'},
            "conversion":   {"current": '--',  "total": '--'}
        },
        "control": {
            "mode":                     None,
            "id_source":                None,
            "run_until":                None,
            "start_button":             'start'
        },
        "settings": {
            "convert_to_webp":          True,   # Checkbox
            "deleter_after_archiving":  True,   # Checkbox
            "save_live_progress":       False,  # Checkbox
            "webp_quality":             None,   # Text input, default set in html
            "cbz_quality":              None,   # Text input, default set in html
            "max_retries":              None    # Text input, default set in html
        },
        "doujin_info": {
            "id":                       "---",
            "title":                    "---",
            "author":                   "---",
            "tags":                     "---"
        },
        "show_cover":                   False,
        "doujin_cover":                 False,
        "task_running":                 False
    }


# Public API: get and initialize full state
def get_full_state() -> dict:
    global _state
    with _lock:
        if _state is None:
            # Initialize in-memory state on first access
            _state = copy.deepcopy(_default_state)
        return _state
    
def get_state(key: str) -> dict:
    global _state
    with _lock:
        if _state is None:
            # Initialize in-memory state on first access
            _state = copy.deepcopy(_default_state)
        return _state[key]

def reset_full_state() -> dict:
    global _state
    with _lock:
        _state = copy.deepcopy(_default_state)
    return get_full_state()

def reset_state(key: str) -> dict:
    global _state
    with _lock:
        _state[key] = copy.deepcopy(_default_state[key])
    return get_full_state()

# Public API: replace or set full state
def set_full_state(state) -> dict:
    global _state
    with _lock:
        _state = state
    return get_full_state()

def set_state(key: str, update: dict = None, subkey: str=None) -> dict:
    global _state
    if not key or update==None:
        return get_full_state()
    if not _state:
        _state = copy.deepcopy(_default_state)
    
    with _lock:
        if subkey:
            _state[key][subkey] = copy.deepcopy(update)
        else:
            _state[key] = copy.deepcopy(update)
    return get_full_state()