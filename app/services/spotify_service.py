import httpx
import os
from dotenv import load_dotenv

load_dotenv()


class SpotifyService:
    API_BASE = "https://api.spotify.com/v1"
    _token = None

    def __init__(self):
        self._token = None

    async def _ensure_token(self):
        if not self._token:
            self._token = await self._get_spotify_token()

    async def _get_spotify_token(self):
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        async with httpx.AsyncClient() as client:
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            }
            response = await client.post(
                "https://accounts.spotify.com/api/token", data=auth_data
            )
            response.raise_for_status()
            return response.json().get("access_token")


spotify_service = SpotifyService()
