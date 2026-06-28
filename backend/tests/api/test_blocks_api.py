from pathlib import Path

import httpx2
import pytest

from app.main import app


async def _make_client():
    transport = httpx2.ASGITransport(app=app)
    return httpx2.AsyncClient(transport=transport, base_url="http://testserver")


@pytest.mark.anyio
async def test_blocks_api_returns_file_blocks_and_block_detail(tmp_path, monkeypatch):
    db_path = tmp_path / "repolens.db"
    monkeypatch.setenv("REPOLENS_DATABASE_PATH", str(db_path))

    repo_dir = tmp_path / "sample_repo"
    repo_dir.mkdir()
    file_path = repo_dir / "main.py"
    file_path.write_text(
        "def run_pipeline(value):\n"
        "    return value\n",
        encoding="utf-8",
    )

    async with await _make_client() as client:
        index_response = await client.post("/api/repos/index-local", json={"path": str(repo_dir)})
        assert index_response.status_code == 200
        repo_id = index_response.json()["repo_id"]

        blocks_response = await client.get(
            f"/api/repos/{repo_id}/files/blocks",
            params={"path": "main.py"},
        )
        assert blocks_response.status_code == 200
        blocks = blocks_response.json()["blocks"]
        assert len(blocks) == 1
        assert blocks[0]["name"] == "run_pipeline"
        assert blocks[0]["block_type"] == "function"

        detail_response = await client.get(f"/api/blocks/{blocks[0]['id']}")
        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert detail["name"] == "run_pipeline"
        assert detail["relative_path"] == "main.py"
        assert detail["content"].startswith("def run_pipeline")
        assert detail["code_hash"]
