"""File filtering stage."""

from __future__ import annotations

import fnmatch
from pathlib import Path

import pathspec

from app.core.config import MAX_FILE_SIZE_BYTES, STATE_FILENAME
from app.models.repo_file import RepoFileRecord

IGNORE_DIRS = {
    ".git",
    ".github",
    "logs",
    "tmp",
    "temp",
    ".serverless",
    "node_modules",
    ".next",
    ".nuxt",
    "dist",
    "build",
    "coverage",
    ".vercel",
    ".netlify",
    ".turbo",
    ".parcel-cache",
    ".cache",
    ".vite",
    "out",
    "venv",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".hypothesis",
    "htmlcov",
    ".eggs",
}

IGNORE_FILENAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "npm-debug.log",
    "yarn-error.log",
    "pnpm-debug.log",
    STATE_FILENAME,
    "Cargo.lock",
    "poetry.lock",
    "Gemfile.lock",
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".env.test",
    ".DS_Store",
    "Thumbs.db",
    ".coverage",
    "coverage.xml",
}

IGNORE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".ico",
    ".sqlite",
    ".sqlite3",
    ".db",
    ".pdf",
    ".svg",
    ".zip",
    ".rar",
    ".tar",
    ".gz",
    ".7z",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".pyc",
    ".pyo",
    ".log",
    ".map",
}

IGNORE_PATTERNS = {
    "*.min.js",
    "*.min.css",
    "*_generated.py",
    "*_pb2.py",
    "*_pb2_grpc.py",
    "*.pb.go",
    "generated/*",
    "gen/*",
    "*.egg-info",
    "*.egg-info/*",
    ".coverage.*",
}


def filter_files(files: list[RepoFileRecord], repo_root: str) -> list[RepoFileRecord]:
    """Apply .gitignore and system ignore rules."""
    spec = _load_gitignore(repo_root)
    filtered: list[RepoFileRecord] = []
    for file in files:
        if spec is not None and spec.match_file(file.relative_path):
            file.skipped = True
            file.skip_reason = "gitignore"
            continue
        if _is_system_ignored(file):
            file.skipped = True
            file.skip_reason = "ignored"
            continue
        filtered.append(file)
    return filtered


def _load_gitignore(repo_root: str):
    gitignore = Path(repo_root) / ".gitignore"
    if not gitignore.exists():
        return None
    with gitignore.open("r", encoding="utf-8", errors="ignore") as handle:
        return pathspec.PathSpec.from_lines("gitwildmatch", handle)


def _is_system_ignored(file: RepoFileRecord) -> bool:
    path = Path(file.relative_path)
    parts = set(path.parts)
    if parts & IGNORE_DIRS:
        return True
    if path.name in IGNORE_FILENAMES:
        return True
    if file.extension.lower() in IGNORE_EXTENSIONS:
        return True
    if MAX_FILE_SIZE_BYTES > 0 and int(file.size_bytes or 0) > MAX_FILE_SIZE_BYTES:
        return True
    return any(fnmatch.fnmatch(file.relative_path, pattern) for pattern in IGNORE_PATTERNS)

