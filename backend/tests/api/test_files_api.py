from pathlib import Path

import httpx2
import pytest

from app.main import app


async def _make_client():
    transport = httpx2.ASGITransport(app=app)
    return httpx2.AsyncClient(transport=transport, base_url="http://testserver")


async def _index_sample_repo(client: httpx2.AsyncClient, repo_dir: Path) -> str:
    response = await client.post(
        "/api/repos/index-local",
        json={"path": str(repo_dir), "name": "sample-repo"},
    )
    assert response.status_code == 200
    return response.json()["repo_id"]


@pytest.mark.anyio
async def test_file_tree_api_returns_hierarchy(tmp_path, monkeypatch):
    db_path = tmp_path / "repolens.db"
    monkeypatch.setenv("REPOLENS_DATABASE_PATH", str(db_path))

    repo_dir = tmp_path / "sample_repo"
    (repo_dir / "backend").mkdir(parents=True)
    (repo_dir / "backend" / "main.py").write_text(
        "def run_pipeline():\n"
        "    return True\n",
        encoding="utf-8",
    )

    async with await _make_client() as client:
        repo_id = await _index_sample_repo(client, repo_dir)

        tree_response = await client.get(f"/api/repos/{repo_id}/files/tree")
        assert tree_response.status_code == 200
        payload = tree_response.json()
        assert payload["repo_id"] == repo_id
        assert payload["tree"][0]["name"] == "backend"
        assert payload["tree"][0]["children"][0]["name"] == "main.py"
        assert payload["tree"][0]["children"][0]["has_blocks"] is True
