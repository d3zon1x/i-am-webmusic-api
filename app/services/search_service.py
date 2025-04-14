import httpx
import os
from dotenv import load_dotenv

load_dotenv()

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")

async def search_song(query: str):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.search",
        "track": query,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": 5
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        tracks = data.get("results", {}).get("trackmatches", {}).get("track", [])

        return tracks
