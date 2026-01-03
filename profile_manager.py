import json
import os

PROFILE_FILE = "profiles.json"

class ProfileManager:
    def __init__(self):
        self.data = self._load_from_disk()

    def _load_from_disk(self):
        # Si no existe, creamos estructura base
        if not os.path.exists(PROFILE_FILE):
            return {"last_profile": "Default", "profiles": {}}
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"last_profile": "Default", "profiles": {}}

    def _save_to_disk(self):
        try:
            with open(PROFILE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving profiles: {e}")

    def get_profile_names(self):
        return list(self.data["profiles"].keys())

    def get_profile_data(self, name):
        return self.data["profiles"].get(name, None)

    def save_profile(self, name, settings_dict):
        self.data["profiles"][name] = settings_dict
        self.data["last_profile"] = name
        self._save_to_disk()

    def delete_profile(self, name):
        if name in self.data["profiles"]:
            del self.data["profiles"][name]
            # Si borramos el actual, reseteamos el 'last_profile'
            if self.data["last_profile"] == name:
                keys = list(self.data["profiles"].keys())
                self.data["last_profile"] = keys[0] if keys else None
            self._save_to_disk()

    def get_last_used_profile_name(self):
        return self.data.get("last_profile", None)

    def set_last_used(self, name):
        self.data["last_profile"] = name
        self._save_to_disk()