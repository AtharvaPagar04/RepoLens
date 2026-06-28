"""Generic repo path normalization helpers."""

from __future__ import annotations

from pathlib import Path, PurePosixPath
import re

_BLOCK_SUFFIX_RE = re.compile(r"(\.[A-Za-z0-9]{1,8}):block_[A-Za-z0-9_-]+$")


def normalize_repo_path(path: str, repo_root: str | None = None) -> str:
    """Convert a file path into a stable repo-relative POSIX path when possible."""
    raw = str(path or "").strip().strip("\"'`")
    if not raw:
        return ""

    raw = _BLOCK_SUFFIX_RE.sub(r"\1", raw)
    raw = raw.replace("\\", "/")
    raw = re.sub(r"/+", "/", raw)

    normalized_root = ""
    if repo_root:
        normalized_root = str(repo_root).strip().replace("\\", "/").rstrip("/")
        if normalized_root:
            normalized_root = re.sub(r"/+", "/", normalized_root)
            if raw == normalized_root:
                return ""
            prefix = f"{normalized_root}/"
            if raw.startswith(prefix):
                raw = raw[len(prefix):]

    if raw.startswith("./"):
        raw = raw[2:]

    is_absolute = raw.startswith("/")
    drive_match = re.match(r"^[A-Za-z]:/", raw)
    parts: list[str] = []
    for piece in raw.split("/"):
        if not piece or piece == ".":
            continue
        if piece == "..":
            if parts and parts[-1] != "..":
                parts.pop()
            elif not is_absolute and not drive_match:
                parts.append(piece)
            continue
        parts.append(piece)

    normalized = PurePosixPath(*parts).as_posix() if parts else ""
    if normalized == ".":
        return ""
    if normalized_root and normalized.startswith("../"):
        return ""
    return normalized


def path_metadata(path: str, repo_root: str | None = None) -> dict[str, str]:
    """Return normalized path metadata."""
    normalized = normalize_repo_path(path, repo_root=repo_root)
    effective = normalized or str(path or "").strip().replace("\\", "/").rstrip("/")
    filename = PurePosixPath(effective).name if effective else ""
    extension = PurePosixPath(filename).suffix if filename else ""
    basename = filename[: -len(extension)] if filename and extension else filename
    return {
        "normalized_path": normalized,
        "filename": filename,
        "basename": basename,
        "extension": extension,
    }


def resolve_repo_relative_path(repo_root: str | Path, path: str) -> str:
    """Best-effort repo-relative normalization for discovery and persistence."""
    return normalize_repo_path(path, repo_root=str(Path(repo_root).resolve()))

