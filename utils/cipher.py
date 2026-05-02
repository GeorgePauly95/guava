import os
import hmac
import hashlib
from cryptography.fernet import Fernet

state_key = os.getenv("STATE_KEY")

cipher = Fernet(state_key.encode())

secret_key = os.getenv("SECRET_KEY").encode("utf-8")


def create_signature(message: str):
    signature = hmac.new(secret_key, message.encode("utf-8"), hashlib.sha256).digest()
    return signature
