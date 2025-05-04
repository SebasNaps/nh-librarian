import json
from pathlib import Path
from threading import Lock
from options import *

class Settings:
    _lock = Lock()
    
    # Define default settings
    _defaults = {
        "convert_to_webp": True,
        "delete_after_archiving": False,
        "save_live_progress": True,
        "webp_quality": 85,
        "cbz_quality": 6,
        "max_retries": 3
    }

    def __init__(self, filepath: str = f"{CONFIG_DIR}/{SETTINGS_FILE}"):
        self.path = Path(filepath)
        self._data = {}
        self.load()

    def load(self):
        """Load settings from file, fallback to defaults if not present."""
        if self.path.exists():
            try:
                with self.path.open('r', encoding='utf-8') as f:
                    self._data = json.load(f)
                # Merge missing defaults
                for key, value in self._defaults.items():
                    self._data.setdefault(key, value)
            except Exception as e:
                print(f"Failed to load settings: {e}")
                self._data = self._defaults.copy()
        else:
            self._data = self._defaults.copy()
            self.save()

    def save(self):
        """Save current settings to file."""
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)  # Ensure folder exists
            with self.path.open('w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=4)

    def reset(self):
        """Reset settings to defaults."""
        with self._lock:
            self._data = self._defaults.copy()
        self.save()

    def get(self, key: str):
        """Get a setting value."""
        return self._data.get(key, self._defaults.get(key))

    def set(self, key: str, value):
        """Set a setting value."""
        with self._lock:
            self._data[key] = value
        self.save()

    def all(self):
        """Return all current settings."""
        return self._data.copy()
