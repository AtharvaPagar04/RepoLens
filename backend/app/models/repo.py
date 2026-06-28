"""Repo model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RepoRecord:
    id: str
    name: str
    source_url: str | None
    local_path: str
    created_at: str
    updated_at: str

