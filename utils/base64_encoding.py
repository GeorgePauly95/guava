import base64


def base64url_encode(data: bytes) -> str:
    encoded_data = base64.urlsafe_b64encode(data)
    return encoded_data.rstrip(b"=").decode("utf-8")
