import json
import os
from pathlib import Path


class ConfigManager:
    """Manages application configuration and language localization."""

    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self.settings = {}
        self.translations = {}
        self.current_lang = "en"
        self._load_config()
        self._load_language(self.settings.get("language", "en"))

    def _load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.settings = json.load(f)
        else:
            self.settings = self._default_config()
            self._save_config()

    def _default_config(self):
        return {
            "app_name": "DeviceForge Pro",
            "version": "1.0.0",
            "language": "en",
            "theme": "dark",
            "adb_path": "tools/adb.exe",
            "fastboot_path": "tools/fastboot.exe",
            "plugin_dir": "plugins",
            "log_dir": "logs",
            "download_dir": "downloads",
            "backup_dir": "backups",
            "max_retries": 3,
            "timeout": 30
        }

    def _save_config(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)

    def _load_language(self, lang_code):
        lang_path = f"config/languages/{lang_code}.json"
        if os.path.exists(lang_path):
            with open(lang_path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
            self.current_lang = lang_code
        else:
            self.translations = {}
            self.current_lang = "en"

    def set_language(self, lang_code):
        self.settings["language"] = lang_code
        self._save_config()
        self._load_language(lang_code)

    def get(self, key, fallback=""):
        return self.translations.get(key, fallback)

    def get_setting(self, key, fallback=None):
        return self.settings.get(key, fallback)

    def set_setting(self, key, value):
        self.settings[key] = value
        self._save_config()

    def get_available_languages(self):
        lang_dir = Path("config/languages")
        if not lang_dir.exists():
            return {"en": "English"}
        langs = {}
        for f in lang_dir.glob("*.json"):
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    name = data.get("app_title", f.stem)
                    langs[f.stem] = name
            except Exception:
                langs[f.stem] = f.stem
        return langs
