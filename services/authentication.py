import json
import base64
from datetime import datetime, timedelta
from .utils import (
    create_jwt_header,
    create_signature,
    base64url_encode,
    get_expiry_time,
    get_user,
    pad_payload,
)


def create_jwt(user_id):
    header = create_jwt_header()
    payload = json.dumps(
        {"sub": user_id, "exp": (datetime.now() + timedelta(hours=24)).timestamp()}
    )
    encoded_header, encoded_payload = (
        base64url_encode(header.encode("utf-8")),
        base64url_encode(payload.encode("utf-8")),
    )
    message = encoded_header + "." + encoded_payload
    encoded_signature = base64url_encode(create_signature(message))
    jwt = encoded_header + "." + encoded_payload + "." + encoded_signature
    return jwt


def verify_jwt(jwt):
    encoded_header, encoded_payload, received_signature = jwt.split(".")
    message = encoded_header + "." + encoded_payload
    encoded_signature = base64url_encode(create_signature(message))
    if encoded_signature != received_signature:
        return
    padded_payload = pad_payload(encoded_payload)
    decoded_payload = json.loads(base64.urlsafe_b64decode(padded_payload))
    if get_expiry_time(decoded_payload) < datetime.now().timestamp():
        return
    return get_user(decoded_payload)
