"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import engine
from .models.base import Base
from .routers import auth, posts, comments, categories, pages

BASE_DIR = Path(__file__).resolve().parent.parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Blog API",
    description="A RESTful blog backend built with FastAPI + SQLAlchemy + JWT",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(pages.router)       # HTML pages first (catch root /)
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(categories.router)
