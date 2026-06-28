from pathlib import Path

from app.db.repositories import get_blocks_for_file, get_files_for_repo
from app.ingestion.pipeline import index_local_repository


def test_pipeline_reindex_reuses_repo_and_replaces_file_blocks(tmp_path: Path, monkeypatch):
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

    first = index_local_repository(str(repo_dir), name="sample-repo")
    first_repo_id = first["repo"]["id"]

    assert first["stats"]["files_indexed"] >= 1
    assert first["stats"]["blocks_extracted"] >= 1

    first_files = get_files_for_repo(first_repo_id)
    first_blocks = get_blocks_for_file(first_repo_id, "app.py")

    assert len(first_files) == 1
    assert first_files[0]["relative_path"] == "app.py"
    assert len([block for block in first_blocks if block["name"] == "greet"]) == 1
    first_greet = next(block for block in first_blocks if block["name"] == "greet")
    assert first_greet["code_hash"]
    assert 'return f"Hello {name}"' in first_greet["content"]

    app_file.write_text(
        "def greet(name):\n"
        "    return f\"Hi {name}\"\n\n"
        "def farewell(name):\n"
        "    return f\"Bye {name}\"\n",
        encoding="utf-8",
    )

    second = index_local_repository(str(repo_dir), name="sample-repo")
    second_repo_id = second["repo"]["id"]

    assert second_repo_id == first_repo_id
    assert second["stats"]["files_indexed"] >= 1
    assert second["stats"]["blocks_extracted"] >= 2

    second_files = get_files_for_repo(second_repo_id)
    second_blocks = get_blocks_for_file(second_repo_id, "app.py")

    assert len(second_files) == 1
    assert second_files[0]["relative_path"] == "app.py"
    assert len(second_blocks) == 2

    greet_blocks = [block for block in second_blocks if block["name"] == "greet"]
    farewell_blocks = [block for block in second_blocks if block["name"] == "farewell"]

    assert len(greet_blocks) == 1
    assert len(farewell_blocks) == 1
    assert 'return f"Hi {name}"' in greet_blocks[0]["content"]
    assert 'return f"Hello {name}"' not in greet_blocks[0]["content"]
    assert greet_blocks[0]["code_hash"] != first_greet["code_hash"]
    assert 'return f"Bye {name}"' in farewell_blocks[0]["content"]


def test_pipeline_reindex_removes_deleted_files_and_blocks(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "repolens.db"
    monkeypatch.setenv("REPOLENS_DATABASE_PATH", str(db_path))

    repo_dir = tmp_path / "sample_repo"
    repo_dir.mkdir()
    app_file = repo_dir / "app.py"
    old_file = repo_dir / "old.py"
    app_file.write_text(
        "def active():\n"
        "    return \"active\"\n",
        encoding="utf-8",
    )
    old_file.write_text(
        "def old_function():\n"
        "    return \"old\"\n",
        encoding="utf-8",
    )

    first = index_local_repository(str(repo_dir), name="sample-repo")
    repo_id = first["repo"]["id"]

    first_files = get_files_for_repo(repo_id)
    first_file_paths = {item["relative_path"] for item in first_files}
    app_blocks_before = get_blocks_for_file(repo_id, "app.py")
    old_blocks_before = get_blocks_for_file(repo_id, "old.py")

    assert first_file_paths == {"app.py", "old.py"}
    assert any(block["name"] == "active" for block in app_blocks_before)
    assert any(block["name"] == "old_function" for block in old_blocks_before)

    old_file.unlink()

    second = index_local_repository(str(repo_dir), name="sample-repo")
    assert second["repo"]["id"] == repo_id

    second_files = get_files_for_repo(repo_id)
    second_file_paths = {item["relative_path"] for item in second_files}
    app_blocks_after = get_blocks_for_file(repo_id, "app.py")
    old_blocks_after = get_blocks_for_file(repo_id, "old.py")

    assert second_file_paths == {"app.py"}
    assert "old.py" not in second_file_paths
    assert any(block["name"] == "active" for block in app_blocks_after)
    assert old_blocks_after == []
