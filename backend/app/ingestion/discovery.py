"""File discovery stage."""

from __future__ import annotations

import os
from pathlib import Path

from app.core.paths import resolve_repo_relative_path
from app.models.repo_file import RepoFileRecord


def discover_files(repository_root: str) -> list[RepoFileRecord]:
    """Walk a repository and return every file as a RepoFileRecord."""
    root = Path(repository_root).resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Repository root does not exist or is not a directory: {root}")

    files: list[RepoFileRecord] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for filename in filenames:
            path = Path(dirpath) / filename
            relative_path = resolve_repo_relative_path(root, str(path))
            stat = path.stat()
            files.append(
                RepoFileRecord(
                    path=str(path.resolve()),
                    relative_path=relative_path,
                    extension=path.suffix,
                    size_bytes=stat.st_size,
                )
            )
    return files

