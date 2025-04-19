# app/services/download_service.py

import yt_dlp
import os
from yt_dlp import YoutubeDL


CACHE_DIR = "audio_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def download_audio(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    file_path = f"../../audio_cache/{video_id}.mp3"


    # Перевірка, чи файл вже існує
    if os.path.exists(file_path):
        return file_path

    # Завантажуємо аудіо файл
    with yt_dlp.YoutubeDL({'format': 'bestaudio'}) as ydl:
        ydl.download([url])

    return file_path


def get_audio_file(video_id: str) -> str:
    file_path = os.path.join(CACHE_DIR, f"{video_id}")
    if os.path.exists(file_path):
        return file_path

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': file_path,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f'https://www.youtube.com/watch?v={video_id}'])

    return f"{file_path}.mp3"