"""Repo indexing endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.repositories import delete_repo, get_repo, get_repo_summary, list_repos
from app.ingestion.pipeline import index_github_repository, index_local_repository

router = APIRouter(prefix="/api/repos", tags=["repos"])


class IndexLocalRequest(BaseModel):
    path: str
    name: str | None = None


class ImportGitHubRequest(BaseModel):
    repo_url: str
    name: str | None = None


@router.post("/index-local")
async def index_local(body: IndexLocalRequest) -> dict:
    result = _run_index_operation(index_local_repository, body.path, body.name)
    return _format_index_response(result)


@router.post("/import-github")
async def import_github(body: ImportGitHubRequest) -> dict:
    result = _run_index_operation(index_github_repository, body.repo_url, body.name)
    response = _format_index_response(result)
    response["local_path"] = result["repo"]["local_path"]
    return response


@router.get("")
async def list_repo_entries() -> dict:
    return {"repos": list_repos()}


@router.get("/{repo_id}")
async def get_repo_entry(repo_id: str) -> dict:
    repo = get_repo_summary(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    return repo


@router.post("/{repo_id}/reindex")
async def reindex_repo(repo_id: str) -> dict:
    repo = get_repo(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    result = _run_index_operation(index_local_repository, repo["local_path"], repo["name"])
    return _format_index_response(result)


@router.delete("/{repo_id}")
async def delete_repo_entry(repo_id: str) -> dict:
    if not delete_repo(repo_id):
        raise HTTPException(status_code=404, detail="Repo not found")
    return {"repo_id": repo_id, "status": "deleted"}


def _run_index_operation(indexer, source: str, name: str | None) -> dict:
    try:
        return indexer(source, name=name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail="Indexing failed") from exc


def _format_index_response(result: dict) -> dict:
    return {
        "repo_id": result["repo"]["id"],
        "status": "indexed",
        "stats": result["stats"],
    }
