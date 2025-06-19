from fastapi import APIRouter, Query
from app.services.search_service import search_song

router = APIRouter(tags=["Search"])

@router.get("/search")
async def search(q: str = Query(..., description="Назва пісні або артист")):
    results = await search_song(q)
    return {"query": q, "results": results}
