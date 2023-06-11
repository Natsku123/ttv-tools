import requests
from config import settings


def get_twitch_access_token() -> str:
    token_res = requests.post(f"{settings.TWITCH_ID_URL}/token", headers={
        "Content-Type": "application/x-www-form-urlencoded"
    }, params={
        "client_id": settings.TWITCH_CLIENT_ID,
        "client_secret": settings.TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }).json()
    return token_res["access_token"]


def get_twitch_headers() -> dict:
    token = get_twitch_access_token()

    return {
        "Authorization": f"Bearer {token}",
        "Client-Id": settings.TWITCH_CLIENT_ID,
    }
