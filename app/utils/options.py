import json
import os

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "settings.json")

DEFAULT_SETTINGS = {
    "security_mode": "Fermer auto",
}

class _Settings:
    def __init__(self):
        self._settings = self._load()

    def _load(self):
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {**DEFAULT_SETTINGS, **data}
            except json.JSONDecodeError:
                print("⚠️ settings.json corrompu. Réinitialisation.")
        return DEFAULT_SETTINGS.copy()

    def save(self):
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        return self._settings.get(key, default)

    def set(self, key, value):
        self._settings[key] = value
        self.save()

    def all(self):
        return self._settings

settings = _Settings()
