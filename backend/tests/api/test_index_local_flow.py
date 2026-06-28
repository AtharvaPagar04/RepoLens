from pathlib import Path

import httpx2
import pytest

from app.main import app


FIXTURE_REPO = Path(__file__).resolve().parents[1] / "fixtures" / "sample_repo"


async def _make_client():
    transport = httpx2.ASGITransport(app=app)
    return httpx2.AsyncClient(transport=transport, base_url="http://testserver")


@pytest.mark.anyio
async def test_index_local_flow_with_fixture_repo(tmp_path, monkeypatch):
    db_path = tmp_path / "repolens.db"
    monkeypatch.setenv("REPOLENS_DATABASE_PATH", str(db_path))

    async with await _make_client() as client:
        index_response = await client.post(
            "/api/repos/index-local",
            json={"path": str(FIXTURE_REPO), "name": "fixture-repo"},
        )
        assert index_response.status_code == 200
        payload = index_response.json()

        assert payload["repo_id"]
        assert payload["status"] == "indexed"
        assert payload["stats"]["files_discovered"] >= 4
        assert payload["stats"]["files_indexed"] >= 3
        assert payload["stats"]["blocks_extracted"] >= 4

        repo_id = payload["repo_id"]

        tree_response = await client.get(f"/api/repos/{repo_id}/files/tree")
        assert tree_response.status_code == 200
        tree_payload = tree_response.json()
        assert tree_payload["tree"]

        names_by_path = set()

        def walk(nodes):
            for node in nodes:
                names_by_path.add(node["path"])
                if node["type"] == "directory":
                    walk(node["children"])

        walk(tree_payload["tree"])
        assert "app.py" in names_by_path
        assert "utils.py" in names_by_path
        assert "components/Login.tsx" in names_by_path
        assert "node_modules/ignored.js" not in names_by_path

        blocks_response = await client.get(
            f"/api/repos/{repo_id}/files/blocks",
            params={"path": "app.py"},
        )
        assert blocks_response.status_code == 200
        blocks_payload = blocks_response.json()
        assert blocks_payload["blocks"]
        assert any(block["block_type"] in {"function", "class", "method"} for block in blocks_payload["blocks"])

        block_id = blocks_payload["blocks"][0]["id"]
        detail_response = await client.get(f"/api/blocks/{block_id}")
        assert detail_response.status_code == 200
        detail_payload = detail_response.json()
        assert detail_payload["content"]
        assert detail_payload["start_line"] >= 1
        assert detail_payload["end_line"] >= detail_payload["start_line"]
        assert detail_payload["code_hash"]
