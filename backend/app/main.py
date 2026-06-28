"""FastAPI app entrypoint for RepoLens."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.blocks import router as blocks_router
from app.api.files import router as files_router
from app.api.repos import router as repos_router
from app.core.config import ALLOWED_CORS_ORIGINS
from app.db.database import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="RepoLens", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(repos_router)
app.include_router(files_router)
app.include_router(blocks_router)
