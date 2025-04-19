# app/api/music.py

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse

from app.services.donwload_service import get_audio_file
from app.services.youtube_service import search_youtube_music

router = APIRouter(prefix="/music", tags=["Music"])

@router.get("/search")
def search_music(query: str = Query(..., min_length=1)):
    return search_youtube_music(query)

@router.get("/stream/{video_id}")
async def stream_audio(video_id: str):
    try:
        file_path = get_audio_file(video_id)
        return FileResponse(file_path, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
