from fastapi import APIRouter, HTTPException
from ..services.spotify_service import spotify_service, SpotifyService
import httpx

router = APIRouter(tags=["Artistç"])


@router.get("/artist/{artist_name}")
async def get_artist_by_name(artist_name: str, market: str = "US"):
    await spotify_service._ensure_token()
    headers = {"Authorization": f"Bearer {spotify_service._token}"}

    async with httpx.AsyncClient() as client:
        search_res = await client.get(
            f"{spotify_service.API_BASE}/search",
            headers=headers,
            params={"q": artist_name, "type": "artist", "limit": 1}
        )
        if search_res.status_code != 200:
            raise HTTPException(status_code=404, detail="Artist not found")

        search_data = search_res.json()
        artists = search_data.get("artists", {}).get("items", [])
        if not artists:
            raise HTTPException(status_code=404, detail="Artist not found")

        artist = artists[0]
        artist_id = artist["id"]

        res_artist = await client.get(
            f"{spotify_service.API_BASE}/artists/{artist_id}",
            headers=headers,
            params={"market": market}
        )
        if res_artist.status_code != 200:
            raise HTTPException(status_code=404, detail="Artist details not found")
        artist = res_artist.json()

        res_top = await client.get(
            f"{spotify_service.API_BASE}/artists/{artist_id}/top-tracks",
            headers=headers,
            params={"market": market}
        )
        top_tracks = res_top.json().get("tracks", [])

        res_albums = await client.get(
            f"{spotify_service.API_BASE}/artists/{artist_id}/albums",
            headers=headers,
            params={"market": market, "include_groups": "album,single", "limit": 50}
        )
        albums = res_albums.json().get("items", [])

    albums = sorted({a["name"]: a for a in albums}.values(), key=lambda x: x["release_date"], reverse=True)

    return {
        "artist": {
            "id": artist["id"],
            "name": artist["name"],
            "photo": artist["images"][0]["url"] if artist["images"] else None,
        },
        "topTracks": [
            {
                "id": t["id"],
                "title": t["name"],
                "artist": ", ".join(a["name"] for a in t["artists"]),
                "thumbnail": t["album"]["images"][1]["url"] if len(t["album"]["images"]) > 1 else
                t["album"]["images"][0]["url"],
                "duration_ms": t["duration_ms"],
                "preview_url": t["preview_url"],
            }
            for t in top_tracks[:10]
        ],
        "albums": [
            {
                "id": alb["id"],
                "name": alb["name"],
                "type": alb["album_type"],  # "album" чи "single"
                "photo": alb["images"][1]["url"] if len(alb["images"]) > 1 else alb["images"][0]["url"],
                "release_date": alb["release_date"],
            }
            for alb in albums
        ]
    }

# Отримуємо треки з альбому
@router.get("/album/{album_id}/tracks")
async def get_tracks_from_album(album_id: str, market: str = "US"):
    await spotify_service._ensure_token()
    headers = {"Authorization": f"Bearer {spotify_service._token}"}

    async with httpx.AsyncClient() as client:
        res_album = await client.get(
            f"{spotify_service.API_BASE}/albums/{album_id}",
            headers=headers,
            params={"market": market}
        )
        if res_album.status_code != 200:
            raise HTTPException(status_code=404, detail="Album not found")
        album = res_album.json()

        res_tracks = await client.get(
            f"{spotify_service.API_BASE}/albums/{album_id}/tracks",
            headers=headers,
            params={"market": market}
        )
        if res_tracks.status_code != 200:
            raise HTTPException(status_code=404, detail="Tracks not found")
        tracks = res_tracks.json().get("items", [])

    formatted_tracks = [
        {
            "id": track["id"],
            "title": track["name"],
            "artist": ", ".join(a["name"] for a in track["artists"]),
            # "thumbnail": track["album"]["images"][1]["url"] if len(track["album"]["images"]) > 1 else track["album"]["images"][0]["url"],
            "duration_ms": track["duration_ms"],
            "preview_url": track["preview_url"],
        }
        for track in tracks
    ]

    return {
        "album": {
            "id": album["id"],
            "name": album["name"],
            "type": album["album_type"],
            "photo": album["images"][1]["url"] if len(album["images"]) > 1 else album["images"][0]["url"],
            "release_date": album["release_date"],
        },
        "tracks": formatted_tracks,
    }