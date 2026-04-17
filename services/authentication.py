import base64
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import json

load_dotenv()

secret_key = os.getenv("SECRET_KEY").encode("utf-8")


# TODO: why are both base64url_encode and base64.urlsafe_b64encode being used.
def base64url_encode(data: bytes) -> str:
    encoded_data = base64.urlsafe_b64encode(data)
    return encoded_data.rstrip(b"=").decode("utf-8")


def create_jwt(user_id, secret_key):
    header = json.dumps({"alg": "HS256", "typ": "JWT"})
    payload = json.dumps(
        {"sub": user_id, "exp": (datetime.now() + timedelta(hours=24)).timestamp()}
    )
    encoded_header, encoded_payload = (
        base64url_encode(header.encode("utf-8")),
        base64url_encode(payload.encode("utf-8")),
    )
    message = encoded_header + "." + encoded_payload
    signature = hmac.new(secret_key, message.encode("utf-8"), hashlib.sha256).digest()
    encoded_signature = base64url_encode(signature)
    jwt = encoded_header + "." + encoded_payload + "." + encoded_signature
    return jwt


def verify_jwt(jwt):
    encoded_header, encoded_payload, received_signature = jwt.split(".")
    message = encoded_header + "." + encoded_payload
    signature = hmac.new(secret_key, message.encode("utf-8"), hashlib.sha256).digest()
    encoded_signature = base64url_encode(signature)
    if encoded_signature != received_signature:
        return "Rejected"
    padded_payload = encoded_payload + "=" * (-len(encoded_payload) % 4)
    decoded_payload = json.loads(base64.urlsafe_b64decode(padded_payload))
    if decoded_payload["exp"] < datetime.now().timestamp():
        return "Rejected"
    return decoded_payload["sub"]
