import os
import httpx
from .authentication import create_jwt
from models import Users

google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
google_scope = os.getenv("GOOGLE_SCOPE")
google_redirect_url = os.getenv("REDIRECT_URL")
google_auth_url = os.getenv("GOOGLE_AUTH_URL")
google_token_url = os.getenv("GOOGLE_TOKEN_URL")
google_user_info_url = os.getenv("GOOGLE_USER_INFO_URL")
google_oauth_url = f"{google_auth_url}?client_id={google_client_id}&redirect_uri={google_redirect_url}&scope={google_scope}&response_type=code"

GRANT_TYPE = "authorization_code"


def get_access_token(code):
    request_body = {
        "code": code,
        "client_id": google_client_id,
        "client_secret": google_client_secret,
        "redirect_uri": google_redirect_url,
        "grant_type": GRANT_TYPE,
    }
    token_response = httpx.post(google_token_url, data=request_body)
    token_response_body = token_response.json()
    access_token = token_response_body.get("access_token")
    return access_token


def get_user_info(access_token):
    user_info_response = httpx.get(
        google_user_info_url, headers={"Authorization": f"Bearer {access_token}"}
    )
    return user_info_response.json()


def get_google_id(user_info):
    return user_info["id"]


def get_google_email(user_info):
    return user_info["email"]


def handle_google_oauth(code):
    access_token = get_access_token(code)
    user_info = get_user_info(access_token)
    google_id, google_username = get_google_id(user_info), get_google_email(user_info)
    user_id = Users.get_or_create_by_google_id(google_id, google_username)
    jwt = create_jwt(user_id)
    return jwt
