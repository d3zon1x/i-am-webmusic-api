
from    ytmusicapi import YTMusic

yt = YTMusic()

def search_youtube_music(query: str):
    results = yt.search(query, filter="songs")  # можна ще 'videos', 'albums', 'artists'
    return results