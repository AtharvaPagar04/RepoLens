"""Repository loading helpers."""

from __future__ import annotations

from pathlib import Path
import re
from urllib.parse import urlparse

from app.core.config import REPO_STORAGE_DIR

GITHUB_HOSTS = {"github.com", "www.github.com"}


def load_local_repository(source: str, name: str | None = None) -> dict:
    """Resolve a local repository path for Phase 1 indexing."""
    source_path = Path(source).expanduser()
    if not source_path.exists():
        raise FileNotFoundError(f"Path does not exist: {source_path}")
    if not source_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {source_path}")

    repository_root = source_path.resolve()
    return {
        "repository_name": name or repository_root.name,
        "repository_root": str(repository_root),
        "source_type": "local",
        "source_url": None,
    }


def load_github_repository(source_url: str, name: str | None = None) -> dict:
    """Validate and clone or reuse a GitHub repository for indexing."""
    return clone_github_repository(source_url, name=name)


def clone_github_repository(source_url: str, name: str | None = None) -> dict:
    """Clone a GitHub repository into the configured RepoLens storage dir."""
    owner, repo_slug, normalized_url = validate_github_url(source_url)
    try:
        from git import Repo
    except Exception as exc:  # pragma: no cover - depends on optional install
        raise RuntimeError(
            "GitPython is required for GitHub cloning but is not installed."
        ) from exc

    repo_name = name or repo_slug
    destination_name = sanitize_repo_directory_name(f"{owner}_{repo_slug}")
    destination = (REPO_STORAGE_DIR / destination_name).resolve()
    if destination.exists():
        if not destination.is_dir():
            raise RuntimeError(f"Clone destination exists and is not a directory: {destination}")
        return {
            "repository_name": repo_name,
            "repository_root": str(destination),
            "source_type": "github",
            "source_url": normalized_url,
        }

    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        Repo.clone_from(normalized_url, destination)
    except Exception as exc:  # pragma: no cover - external dependency
        raise RuntimeError(f"Failed to clone repository: {exc}") from exc

    return {
        "repository_name": repo_name,
        "repository_root": str(destination),
        "source_type": "github",
        "source_url": normalized_url,
    }


def validate_github_url(source_url: str) -> tuple[str, str, str]:
    parsed = urlparse(source_url.strip())
    if parsed.scheme not in {"http", "https"} or parsed.netloc not in GITHUB_HOSTS:
        raise ValueError("Unsupported GitHub URL")

    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) != 2:
        raise ValueError("Unsupported GitHub URL")

    owner, repo_part = parts
    repo_slug = repo_part.removesuffix(".git").strip()
    if not owner or not repo_slug:
        raise ValueError("Unsupported GitHub URL")

    return owner, repo_slug, f"https://github.com/{owner}/{repo_slug}.git"


def sanitize_repo_directory_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-._")
    return cleaned or "repository"
