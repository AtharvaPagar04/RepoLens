"""Hashing and light ingestion-state helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.core.config import STATE_FILENAME
from app.models.repo_file import RepoFileRecord


def hash_content(content: str) -> str:
    return hashlib.sha256((content or "").encode("utf-8")).hexdigest()


def hash_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_ingestion_state(repository_root: str) -> dict[str, dict[str, int]]:
    state_path = Path(repository_root) / STATE_FILENAME
    if not state_path.exists():
        return {}
    with state_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        return {}
    state: dict[str, dict[str, int]] = {}
    for relative_path, signature in data.items():
        if isinstance(signature, dict):
            size = int(signature.get("size_bytes", -1))
            mtime = int(signature.get("mtime_ns", -1))
            if size >= 0 and mtime >= 0:
                state[str(relative_path)] = {"size_bytes": size, "mtime_ns": mtime}
    return state


def save_ingestion_state(repository_root: str, state: dict[str, dict[str, int]]) -> None:
    state_path = Path(repository_root) / STATE_FILENAME
    with state_path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)


def build_file_signature(file: RepoFileRecord) -> dict[str, int]:
    stat = Path(file.path).stat()
    return {"size_bytes": int(file.size_bytes), "mtime_ns": int(stat.st_mtime_ns)}


def is_file_unchanged(
    relative_path: str,
    signature: dict[str, int],
    previous_state: dict[str, dict[str, int]],
) -> bool:
    return previous_state.get(relative_path) == signature

