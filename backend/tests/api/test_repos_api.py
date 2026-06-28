from pathlib import Path

import httpx2
import pytest

from app.main import app


async def _make_client():
    transport = httpx2.ASGITransport(app=app)
    return httpx2.AsyncClient(transport=transport, base_url="http://testserver")


async def _index_repo(client: httpx2.AsyncClient, repo_dir: Path, name: str = "sample-repo") -> str:
    response = await client.post(
        "/api/repos/index-local",
        json={"path": str(repo_dir), "name": name},
    )
    assert response.status_code == 200
    return response.json()["repo_id"]


@pytest.mark.anyio
async def test_repos_api_lists_details_reindexes_and_deletes(tmp_path, monkeypatch):
    db_path = tmp_path / "repolens.db"
    monkeypatch.setenv("REPOLENS_DATABASE_PATH", str(db_path))

    repo_dir = tmp_path / "sample_repo"
    repo_dir.mkdir()
    app_file = repo_dir / "app.py"
    app_file.write_text(
        "def greet(name):\n"
        "    return f\"Hello {name}\"\n",
        encoding="utf-8",
    )

    async with await _make_client() as client:
        repo_id = await _index_repo(client, repo_dir)

        list_response = await client.get("/api/repos")
        assert list_response.status_code == 200
        repos = list_response.json()["repos"]
        assert len(repos) == 1
        assert repos[0]["id"] == repo_id
        assert repos[0]["file_count"] == 1
        assert repos[0]["block_count"] >= 1

        detail_response = await client.get(f"/api/repos/{repo_id}")
        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert detail["id"] == repo_id
        assert detail["name"] == "sample-repo"
        assert detail["local_path"] == str(repo_dir.resolve())
        assert detail["file_count"] == 1
        assert detail["block_count"] >= 1

        app_file.write_text(
            "def greet(name):\n"
            "    return f\"Hi {name}\"\n\n"
            "def farewell(name):\n"
            "    return f\"Bye {name}\"\n",
            encoding="utf-8",
        )
        reindex_response = await client.post(f"/api/repos/{repo_id}/reindex")
        assert reindex_response.status_code == 200
        reindex_payload = reindex_response.json()
        assert reindex_payload["repo_id"] == repo_id
        assert reindex_payload["status"] == "indexed"
        assert reindex_payload["stats"]["blocks_extracted"] >= 2

        blocks_response = await client.get(
            f"/api/repos/{repo_id}/files/blocks",
            params={"path": "app.py"},
        )
        blocks = blocks_response.json()["blocks"]
        assert len([block for block in blocks if block["name"] == "greet"]) == 1
        assert any(block["name"] == "farewell" for block in blocks)

        delete_response = await client.delete(f"/api/repos/{repo_id}")
        assert delete_response.status_code == 200
        assert delete_response.json() == {"repo_id": repo_id, "status": "deleted"}

        missing_detail = await client.get(f"/api/repos/{repo_id}")
        assert missing_detail.status_code == 404
        assert missing_detail.json() == {"detail": "Repo not found"}


@pytest.mark.anyio
async def test_repos_api_handles_invalid_inputs_and_missing_resources(tmp_path, monkeypatch):
    db_path = tmp_path / "repolens.db"
    monkeypatch.setenv("REPOLENS_DATABASE_PATH", str(db_path))

    missing_path = tmp_path / "missing_repo"
    file_path = tmp_path / "not_a_repo.py"
    file_path.write_text("print('hi')\n", encoding="utf-8")

    async with await _make_client() as client:
        missing_response = await client.post(
            "/api/repos/index-local",
            json={"path": str(missing_path)},
        )
        assert missing_response.status_code == 404
        assert missing_response.json() == {"detail": f"Path does not exist: {missing_path}"}

        not_directory_response = await client.post(
            "/api/repos/index-local",
            json={"path": str(file_path)},
        )
        assert not_directory_response.status_code == 400
        assert not_directory_response.json() == {"detail": f"Path is not a directory: {file_path}"}

        missing_repo_response = await client.get("/api/repos/unknown-repo")
        assert missing_repo_response.status_code == 404
        assert missing_repo_response.json() == {"detail": "Repo not found"}

        missing_reindex_response = await client.post("/api/repos/unknown-repo/reindex")
        assert missing_reindex_response.status_code == 404
        assert missing_reindex_response.json() == {"detail": "Repo not found"}

        missing_delete_response = await client.delete("/api/repos/unknown-repo")
        assert missing_delete_response.status_code == 404
        assert missing_delete_response.json() == {"detail": "Repo not found"}

        missing_block_response = await client.get("/api/blocks/unknown-block")
        assert missing_block_response.status_code == 404
        assert missing_block_response.json() == {"detail": "Block not found"}


@pytest.mark.anyio
async def test_repos_api_cors_preflight_allows_vite_origin(tmp_path, monkeypatch):
    db_path = tmp_path / "repolens.db"
    monkeypatch.setenv("REPOLENS_DATABASE_PATH", str(db_path))

    async with await _make_client() as client:
        response = await client.options(
            "/api/repos",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code != 405
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
