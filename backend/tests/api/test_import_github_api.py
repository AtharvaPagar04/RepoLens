from pathlib import Path

import httpx2
import pytest

from app.main import app


async def _make_client():
    transport = httpx2.ASGITransport(app=app)
    return httpx2.AsyncClient(transport=transport, base_url="http://testserver")


@pytest.mark.anyio
async def test_import_github_api_indexes_valid_repo(monkeypatch, tmp_path):
    db_path = tmp_path / "repolens.db"
    clone_dir = tmp_path / "clones" / "owner_repo"
    monkeypatch.setenv("REPOLENS_DATABASE_PATH", str(db_path))

    def fake_index_github_repository(repo_url: str, name: str | None = None) -> dict:
        assert repo_url == "https://github.com/example/project"
        assert name == "example-project"
        return {
            "repo": {
                "id": "repo-123",
                "local_path": str(clone_dir),
            },
            "stats": {
                "files_discovered": 4,
                "files_indexed": 3,
                "files_skipped": 1,
                "blocks_extracted": 6,
                "parse_errors": 0,
            },
        }

    monkeypatch.setattr("app.api.repos.index_github_repository", fake_index_github_repository)

    async with await _make_client() as client:
        response = await client.post(
            "/api/repos/import-github",
            json={
                "repo_url": "https://github.com/example/project",
                "name": "example-project",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["repo_id"] == "repo-123"
    assert payload["status"] == "indexed"
    assert payload["local_path"] == str(clone_dir)
    assert payload["stats"]["files_discovered"] == 4


@pytest.mark.anyio
async def test_import_github_api_rejects_invalid_url(tmp_path, monkeypatch):
    db_path = tmp_path / "repolens.db"
    monkeypatch.setenv("REPOLENS_DATABASE_PATH", str(db_path))

    async with await _make_client() as client:
        response = await client.post(
            "/api/repos/import-github",
            json={"repo_url": "https://gitlab.com/example/project"},
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "Unsupported GitHub URL"}


@pytest.mark.anyio
async def test_import_github_api_returns_clean_clone_failure(tmp_path, monkeypatch):
    db_path = tmp_path / "repolens.db"
    monkeypatch.setenv("REPOLENS_DATABASE_PATH", str(db_path))

    def fake_index_github_repository(_repo_url: str, name: str | None = None) -> dict:
        raise RuntimeError("Failed to clone repository: auth failed")

    monkeypatch.setattr("app.api.repos.index_github_repository", fake_index_github_repository)

    async with await _make_client() as client:
        response = await client.post(
            "/api/repos/import-github",
            json={"repo_url": "https://github.com/example/project.git"},
        )

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to clone repository: auth failed"}
