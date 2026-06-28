import sqlite3
from pathlib import Path

from app.db.database import get_database_path, init_db
from app.db.repositories import (
    create_repo,
    get_block,
    get_blocks_for_file,
    get_files_for_repo,
    get_repo,
    upsert_code_block,
    upsert_repo_file,
)
from app.models.code_block import CodeBlock


def _configure_test_db(monkeypatch, tmp_path: Path) -> Path:
    db_path = tmp_path / "repolens.db"
    monkeypatch.setenv("REPOLENS_DATABASE_PATH", str(db_path))
    return db_path


def _insert_repo_file(repo_id: str, absolute_path: str, content_hash: str = "hash-1") -> dict:
    return upsert_repo_file(
        repo_id=repo_id,
        relative_path="src/main.py",
        absolute_path=absolute_path,
        language="python",
        extension=".py",
        size_bytes=128,
        content_hash=content_hash,
    )


def _build_block(repo_id: str, file_id: str, block_id: str = "block-1") -> CodeBlock:
    return CodeBlock(
        id=block_id,
        repo_id=repo_id,
        file_id=file_id,
        file_path="/tmp/src/main.py",
        relative_path="src/main.py",
        language="python",
        block_type="function",
        name="run_pipeline",
        qualified_name="run_pipeline",
        start_line=1,
        end_line=3,
        signature="def run_pipeline(value):",
        content="def run_pipeline(value):\n    return value\n",
        code_hash="code-hash-1",
        metadata={"kind": "test"},
    )


def test_init_db_creates_required_tables(tmp_path: Path, monkeypatch):
    db_path = _configure_test_db(monkeypatch, tmp_path)

    init_db()

    with sqlite3.connect(str(db_path)) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()
    table_names = {row[0] for row in rows}

    assert {"repos", "repo_files", "code_blocks"}.issubset(table_names)
    assert get_database_path() == db_path.resolve()


def test_create_repo_and_get_repo_round_trip(tmp_path: Path, monkeypatch):
    _configure_test_db(monkeypatch, tmp_path)

    repo = create_repo(
        name="sample-repo",
        local_path="/tmp/sample-repo",
        source_url="https://example.com/sample-repo.git",
    )
    stored = get_repo(repo["id"])

    assert stored is not None
    assert stored["id"] == repo["id"]
    assert stored["name"] == "sample-repo"
    assert stored["source_url"] == "https://example.com/sample-repo.git"
    assert stored["local_path"] == "/tmp/sample-repo"
    assert stored["created_at"]
    assert stored["updated_at"]


def test_repo_file_upsert_updates_without_duplication(tmp_path: Path, monkeypatch):
    _configure_test_db(monkeypatch, tmp_path)
    repo = create_repo(name="sample-repo", local_path="/tmp/sample-repo")

    original = _insert_repo_file(repo["id"], "/tmp/sample-repo/src/main.py", content_hash="hash-1")
    updated = upsert_repo_file(
        repo_id=repo["id"],
        relative_path="src/main.py",
        absolute_path="/tmp/sample-repo-renamed/src/main.py",
        language="python",
        extension=".py",
        size_bytes=256,
        content_hash="hash-2",
    )
    files = get_files_for_repo(repo["id"])

    assert len(files) == 1
    assert updated["id"] == original["id"]
    assert files[0]["relative_path"] == "src/main.py"
    assert files[0]["absolute_path"] == "/tmp/sample-repo-renamed/src/main.py"
    assert files[0]["language"] == "python"
    assert files[0]["extension"] == ".py"
    assert files[0]["size_bytes"] == 256
    assert files[0]["content_hash"] == "hash-2"


def test_code_block_upsert_updates_without_duplication(tmp_path: Path, monkeypatch):
    _configure_test_db(monkeypatch, tmp_path)
    repo = create_repo(name="sample-repo", local_path="/tmp/sample-repo")
    repo_file = _insert_repo_file(repo["id"], "/tmp/sample-repo/src/main.py")

    original_block = _build_block(repo["id"], repo_file["id"], block_id="block-fixed")
    inserted = upsert_code_block(original_block)

    blocks = get_blocks_for_file(repo["id"], "src/main.py")
    detail = get_block(inserted["id"])

    assert len(blocks) == 1
    assert blocks[0]["id"] == "block-fixed"
    assert blocks[0]["name"] == "run_pipeline"
    assert blocks[0]["qualified_name"] == "run_pipeline"
    assert blocks[0]["block_type"] == "function"
    assert blocks[0]["language"] == "python"
    assert blocks[0]["start_line"] == 1
    assert blocks[0]["end_line"] == 3
    assert blocks[0]["content"].startswith("def run_pipeline")
    assert blocks[0]["code_hash"] == "code-hash-1"
    assert detail is not None
    assert detail["metadata"] == {"kind": "test"}

    updated_block = _build_block(repo["id"], repo_file["id"], block_id="block-fixed")
    updated_block.content = "def run_pipeline(value):\n    return value * 2\n"
    updated_block.code_hash = "code-hash-2"
    updated = upsert_code_block(updated_block)
    blocks_after_update = get_blocks_for_file(repo["id"], "src/main.py")
    detail_after_update = get_block(updated["id"])

    assert len(blocks_after_update) == 1
    assert updated["id"] == inserted["id"]
    assert blocks_after_update[0]["content"].endswith("return value * 2\n")
    assert blocks_after_update[0]["code_hash"] == "code-hash-2"
    assert detail_after_update is not None
    assert detail_after_update["content"].endswith("return value * 2\n")
    assert detail_after_update["code_hash"] == "code-hash-2"


def test_repo_isolation_for_files_and_blocks(tmp_path: Path, monkeypatch):
    _configure_test_db(monkeypatch, tmp_path)
    repo_a = create_repo(name="repo-a", local_path="/tmp/repo-a")
    repo_b = create_repo(name="repo-b", local_path="/tmp/repo-b")

    file_a = upsert_repo_file(
        repo_id=repo_a["id"],
        relative_path="app.py",
        absolute_path="/tmp/repo-a/app.py",
        language="python",
        extension=".py",
        size_bytes=64,
        content_hash="hash-a",
    )
    file_b = upsert_repo_file(
        repo_id=repo_b["id"],
        relative_path="app.py",
        absolute_path="/tmp/repo-b/app.py",
        language="python",
        extension=".py",
        size_bytes=96,
        content_hash="hash-b",
    )

    upsert_code_block(
        CodeBlock(
            id="block-a",
            repo_id=repo_a["id"],
            file_id=file_a["id"],
            file_path="/tmp/repo-a/app.py",
            relative_path="app.py",
            language="python",
            block_type="function",
            name="alpha",
            qualified_name="alpha",
            start_line=1,
            end_line=2,
            signature="def alpha():",
            content="def alpha():\n    return 'a'\n",
            code_hash="hash-alpha",
        )
    )
    upsert_code_block(
        CodeBlock(
            id="block-b",
            repo_id=repo_b["id"],
            file_id=file_b["id"],
            file_path="/tmp/repo-b/app.py",
            relative_path="app.py",
            language="python",
            block_type="function",
            name="beta",
            qualified_name="beta",
            start_line=1,
            end_line=2,
            signature="def beta():",
            content="def beta():\n    return 'b'\n",
            code_hash="hash-beta",
        )
    )

    repo_a_files = get_files_for_repo(repo_a["id"])
    repo_b_files = get_files_for_repo(repo_b["id"])
    repo_a_blocks = get_blocks_for_file(repo_a["id"], "app.py")
    repo_b_blocks = get_blocks_for_file(repo_b["id"], "app.py")

    assert len(repo_a_files) == 1
    assert len(repo_b_files) == 1
    assert repo_a_files[0]["absolute_path"] == "/tmp/repo-a/app.py"
    assert repo_b_files[0]["absolute_path"] == "/tmp/repo-b/app.py"
    assert [block["name"] for block in repo_a_blocks] == ["alpha"]
    assert [block["name"] for block in repo_b_blocks] == ["beta"]
