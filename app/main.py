from fastapi import FastAPI
from app.api import search
from app.api import auth
from app.db import Base, engine
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Music API",
    description="API for music download, search, and playing",
    version="0.1.0",
)

origins = [
    "http://localhost:5173",  # фронтенд Vite
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,             # дозволені джерела
    allow_credentials=True,            # дозволити куки/авторизацію
    allow_methods=["*"],               # дозволені HTTP методи
    allow_headers=["*"],               # дозволені заголовки
)

# SEARCH ROUTER
app.include_router(search.router, prefix="/api")

# AUTH ROUTER
app.include_router(auth.router, prefix="/api")