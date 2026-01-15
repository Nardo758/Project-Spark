"""Encryption service for securely storing sensitive data like API keys."""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionService:
    def __init__(self):
        secret_key = os.environ.get("ENCRYPTION_SECRET_KEY", os.environ.get("SESSION_SECRET", "default-dev-key-change-in-production"))
        self.fernet = self._create_fernet(secret_key)
    
    def _create_fernet(self, secret_key: str) -> Fernet:
        salt = b"oppgrid_byok_salt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        return Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        if not plaintext:
            return ""
        encrypted = self.fernet.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        if not ciphertext:
            return ""
        try:
            encrypted = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted = self.fernet.decrypt(encrypted)
            return decrypted.decode()
        except Exception:
            return ""


encryption_service = EncryptionService()
