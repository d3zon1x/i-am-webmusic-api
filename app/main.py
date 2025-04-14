from fastapi import FastAPI
from app.api import search
from app.api import auth
from app.db import Base, engine

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Music API",
    description="API for music download, search, and playing",
    version="0.1.0",
)

# SEARCH ROUTER
app.include_router(search.router, prefix="/api")



# AUTH ROUTER
app.include_router(auth.router, prefix="/api")