import os
import httpx

google_user_info_url = os.getenv("GOOGLE_USER_INFO_URL")


def get_user_info(access_token: str) -> dict:
    user_info_response = httpx.get(
        google_user_info_url, headers={"Authorization": f"Bearer {access_token}"}
    )
    return user_info_response.json()


def get_token_response(google_token_url: str, request_body: dict) -> dict:
    return httpx.post(google_token_url, data=request_body).json()
