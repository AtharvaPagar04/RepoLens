"""Repository file metadata model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RepoFileRecord:
    path: str
    relative_path: str
    extension: str
    size_bytes: int
    language: str = ""
    skipped: bool = False
    skip_reason: str = ""

