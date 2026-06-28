"""Runtime configuration for the Phase 1 RepoLens backend."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_ROOT / "data"
DEFAULT_DATABASE_PATH = DATA_DIR / "repolens.db"
DEFAULT_REPO_STORAGE_DIR = DATA_DIR / "repos"
STATE_FILENAME = ".repolens_ingestion_state.json"


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_csv(name: str, default: list[str]) -> list[str]:
    value = os.getenv(name)
    if value is None:
        return default
    items = [item.strip() for item in value.split(",")]
    return [item for item in items if item]


DATABASE_URL = os.getenv("REPOLENS_DATABASE_URL", "").strip()
DATABASE_PATH = Path(
    os.getenv("REPOLENS_DATABASE_PATH", str(DEFAULT_DATABASE_PATH))
).expanduser()
REPO_STORAGE_DIR = Path(
    os.getenv("REPOLENS_REPO_STORAGE_DIR", str(DEFAULT_REPO_STORAGE_DIR))
).expanduser()
MAX_FILE_SIZE_BYTES = _env_int("REPOLENS_MAX_FILE_SIZE_BYTES", 512_000)
ENABLE_GITHUB_CLONE = _env_bool("REPOLENS_ENABLE_GITHUB_CLONE", False)
ALLOWED_CORS_ORIGINS = _env_csv(
    "REPOLENS_ALLOWED_CORS_ORIGINS",
    [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
)
