import secrets
import json
from typing import Dict, Optional
from pathlib import Path

class APIKeyManager:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.api_keys: Dict[str, str] = self.load_keys()

    def load_keys(self) -> Dict[str, str]:
        if self.storage_path.exists():
            with open(self.storage_path, "r") as file:
                return json.load(file)
        else:
            return {}

    def save_keys(self):
        with open(self.storage_path, "w") as file:
            json.dump(self.api_keys, file)

    def create_api_key(self, email: str) -> str:
        api_key = secrets.token_urlsafe(16)
        self.api_keys[email] = api_key
        self.save_keys()
        return api_key

    def verify_api_key(self, api_key: str) -> bool:
        return api_key in self.api_keys.values()

    def replace_api_key(self, email: str) -> Optional[str]:
        if email in self.api_keys:
            new_api_key = secrets.token_urlsafe(16)
            self.api_keys[email] = new_api_key
            self.save_keys()
            return new_api_key
        return None