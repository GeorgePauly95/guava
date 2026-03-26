import os

google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
google_scope = os.getenv("GOOGLE_SCOPE")
google_redirect_url = os.getenv("REDIRECT_URL")
google_auth_url = os.getenv("GOOGLE_AUTH_URL")
google_token_url = os.getenv("GOOGLE_TOKEN_URL")
google_user_info_url = os.getenv("GOOGLE_USER_INFO_URL")
google_oauth_url = f"{google_auth_url}?client_id={google_client_id}&redirect_uri={google_redirect_url}&scope={google_scope}&response_type=code"
