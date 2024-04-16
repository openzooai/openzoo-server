import secrets
import json
from typing import Dict, Optional
from pathlib import Path
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer


# Security function to access the Bearer token in the header
security = HTTPBearer(auto_error=False)


class APIKeyManager:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.api_keys: Dict[str, dict] = self.load_keys()


    def load_keys(self) -> Dict[str, dict]:
        if self.storage_path.exists():
            with open(self.storage_path, "r") as file:
                return json.load(file)
        else:
            return {}


    def save_keys(self):
        with open(self.storage_path, "w") as file:
            json.dump(self.api_keys, file)


    def create_api_key(self, email: str, initial_balance: float = 25.0) -> str:
        api_key = secrets.token_urlsafe(16)
        self.api_keys[api_key] = {"email": email, "balance": initial_balance}
        self.save_keys()
        return api_key


    def verify_api_key(self, bearer = Depends(security)) -> bool:
        api_key = bearer.credentials
        if not api_key in self.api_keys:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return True


    def replace_api_key(self, email: str) -> Optional[str]:
        for key, details in self.api_keys.items():
            if details['email'] == email:
                new_api_key = secrets.token_urlsafe(16)
                self.api_keys[new_api_key] = {"email": email, "balance": details["balance"]}
                del self.api_keys[key]  # Remove the old key
                self.save_keys()
                return new_api_key
        return None


    def get_balance(self, api_key: str) -> Optional[float]:
        if api_key in self.api_keys:
            return self.api_keys[api_key]['balance']
        return None


    def reduce_balance(self, api_key: str, amount: float) -> bool:
        """
        Reduces the balance for the given api_key by the specified amount.
        
        :param api_key: The API key for which the balance should be reduced.
        :param amount: The amount to reduce from the balance.
        :return: True if the balance was successfully reduced, False otherwise.
        """
        if api_key in self.api_keys and self.api_keys[api_key]['balance'] >= amount:
            self.api_keys[api_key]['balance'] -= amount
            self.save_keys()
            return True
        return False