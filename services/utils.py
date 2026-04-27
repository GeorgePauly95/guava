import os
import json
import hmac
import base64
import hashlib
from dotenv import load_dotenv

load_dotenv()

TOKEN_TYPE = "JWT"
SIGNING_ALGORITHM = "HS256"

secret_key = os.getenv("SECRET_KEY").encode("utf-8")


def create_jwt_header():
    header = json.dumps({"alg": SIGNING_ALGORITHM, "typ": TOKEN_TYPE})
    return header


def create_signature(message: str):
    signature = hmac.new(secret_key, message.encode("utf-8"), hashlib.sha256).digest()
    return signature


def pad_payload(payload):
    padded_payload = payload + "=" * (-len(payload) % 4)
    return padded_payload


def get_expiry_time(payload):
    return payload.get("exp")


def get_user(payload):
    return payload.get("sub")


def base64url_encode(data: bytes) -> str:
    encoded_data = base64.urlsafe_b64encode(data)
    return encoded_data.rstrip(b"=").decode("utf-8")
