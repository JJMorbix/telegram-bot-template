import os
import json
from pathlib import Path
from dotenv import load_dotenv

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        # carica automaticamente .env nella cartella corrente
        load_dotenv()

        self.mode = os.environ.get("BOT_MODE", "dev")
        self.token = os.environ.get("BOT_TOKEN")

        # admins fissi
        self.admins = set(int(a) for a in os.environ.get("ADMINS", "").split(",") if a.strip())

        # allowed_users solo in DEV
        self.allowed_users_file = Path("config/allowed_users.json")
        if self.mode == "dev":
            if not self.allowed_users_file.exists():
                self.allowed_users_file.write_text("[]")
            self._load_allowed_users()
        else:
            self.allowed_users = set()  # in prod non serve

    # ----------------------
    # DEV: gestione utenti abilitati
    # ----------------------
    def _load_allowed_users(self):
        with open(self.allowed_users_file, "r", encoding="utf-8") as f:
            self.allowed_users = set(json.load(f))
        env_allowed = os.environ.get("ALLOWED_USERS", "")
        env_set = set(int(u) for u in env_allowed.split(",") if u.strip())
        self.allowed_users |= env_set

    def _save_allowed_users(self):
        with open(self.allowed_users_file, "w", encoding="utf-8") as f:
            json.dump(list(self.allowed_users), f, indent=2)

    def add_allowed_user(self, user_id: int):
        if self.mode != "dev":
            return
        if user_id not in self.allowed_users:
            self.allowed_users.add(user_id)
            self._save_allowed_users()

    def remove_allowed_user(self, user_id: int):
        if self.mode != "dev":
            return
        if user_id in self.allowed_users:
            self.allowed_users.remove(user_id)
            self._save_allowed_users()