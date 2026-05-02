import json

TOKEN_TYPE = "JWT"
SIGNING_ALGORITHM = "HS256"


def create_jwt_header():
    header = json.dumps({"alg": SIGNING_ALGORITHM, "typ": TOKEN_TYPE})
    return header


def pad_payload(payload):
    padded_payload = payload + "=" * (-len(payload) % 4)
    return padded_payload


def get_expiry_time(payload):
    return payload.get("exp")


def get_user(payload):
    return payload.get("sub")
