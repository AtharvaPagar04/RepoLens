"""Repository persistence helpers."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from app.core.paths import normalize_repo_path
from app.db.database import db_cursor
from app.models.code_block import CodeBlock


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_repo(name: str, local_path: str, source_url: str | None = None) -> dict:
    now = _now()
    with db_cursor() as (_conn, cursor):
        row = cursor.execute(
            "SELECT id, created_at FROM repos WHERE local_path = ? ORDER BY created_at ASC LIMIT 1",
            (local_path,),
        ).fetchone()
        if row:
            repo_id = row["id"]
            cursor.execute(
                """
                UPDATE repos
                SET name = ?, source_url = ?, updated_at = ?
                WHERE id = ?
                """,
                (name, source_url, now, repo_id),
            )
        else:
            repo_id = uuid.uuid4().hex
            cursor.execute(
                """
                INSERT INTO repos (id, name, source_url, local_path, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (repo_id, name, source_url, local_path, now, now),
            )
    return get_repo(repo_id)


def get_repo(repo_id: str) -> dict | None:
    with db_cursor() as (_conn, cursor):
        row = cursor.execute("SELECT * FROM repos WHERE id = ?", (repo_id,)).fetchone()
    return dict(row) if row else None


def get_repo_by_local_path(local_path: str) -> dict | None:
    with db_cursor() as (_conn, cursor):
        row = cursor.execute(
            "SELECT * FROM repos WHERE local_path = ? ORDER BY created_at ASC LIMIT 1",
            (local_path,),
        ).fetchone()
    return dict(row) if row else None


def list_repos() -> list[dict]:
    with db_cursor() as (_conn, cursor):
        rows = cursor.execute(
            """
            SELECT
                r.*,
                (SELECT COUNT(*) FROM repo_files f WHERE f.repo_id = r.id) AS file_count,
                (SELECT COUNT(*) FROM code_blocks b WHERE b.repo_id = r.id) AS block_count
            FROM repos r
            ORDER BY r.updated_at DESC, r.created_at DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_repo_summary(repo_id: str) -> dict | None:
    with db_cursor() as (_conn, cursor):
        row = cursor.execute(
            """
            SELECT
                r.*,
                (SELECT COUNT(*) FROM repo_files f WHERE f.repo_id = r.id) AS file_count,
                (SELECT COUNT(*) FROM code_blocks b WHERE b.repo_id = r.id) AS block_count
            FROM repos r
            WHERE r.id = ?
            """,
            (repo_id,),
        ).fetchone()
    return dict(row) if row else None


def count_repo_files(repo_id: str) -> int:
    with db_cursor() as (_conn, cursor):
        row = cursor.execute(
            "SELECT COUNT(*) AS count FROM repo_files WHERE repo_id = ?",
            (repo_id,),
        ).fetchone()
    return int(row["count"] if row else 0)


def count_repo_blocks(repo_id: str) -> int:
    with db_cursor() as (_conn, cursor):
        row = cursor.execute(
            "SELECT COUNT(*) AS count FROM code_blocks WHERE repo_id = ?",
            (repo_id,),
        ).fetchone()
    return int(row["count"] if row else 0)


def delete_repo(repo_id: str) -> bool:
    with db_cursor() as (_conn, cursor):
        cursor.execute("DELETE FROM repos WHERE id = ?", (repo_id,))
        deleted = cursor.rowcount > 0
    return deleted


def upsert_repo_file(
    repo_id: str,
    relative_path: str,
    absolute_path: str,
    language: str | None,
    extension: str | None,
    size_bytes: int | None,
    content_hash: str | None,
) -> dict:
    relative_path = normalize_repo_path(relative_path)
    now = _now()
    with db_cursor() as (_conn, cursor):
        row = cursor.execute(
            "SELECT id, created_at FROM repo_files WHERE repo_id = ? AND relative_path = ?",
            (repo_id, relative_path),
        ).fetchone()
        if row:
            file_id = row["id"]
            created_at = row["created_at"]
            cursor.execute(
                """
                UPDATE repo_files
                SET absolute_path = ?, language = ?, extension = ?, size_bytes = ?, content_hash = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    absolute_path,
                    language,
                    extension,
                    size_bytes,
                    content_hash,
                    now,
                    file_id,
                ),
            )
        else:
            file_id = uuid.uuid4().hex
            created_at = now
            cursor.execute(
                """
                INSERT INTO repo_files (
                    id, repo_id, relative_path, absolute_path, language, extension,
                    size_bytes, content_hash, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    file_id,
                    repo_id,
                    relative_path,
                    absolute_path,
                    language,
                    extension,
                    size_bytes,
                    content_hash,
                    created_at,
                    now,
                ),
            )
    return get_repo_file(file_id)


def get_repo_file(file_id: str) -> dict | None:
    with db_cursor() as (_conn, cursor):
        row = cursor.execute("SELECT * FROM repo_files WHERE id = ?", (file_id,)).fetchone()
    return dict(row) if row else None


def delete_blocks_for_file(file_id: str) -> None:
    with db_cursor() as (_conn, cursor):
        cursor.execute("DELETE FROM code_blocks WHERE file_id = ?", (file_id,))


def delete_repo_files_missing_from_scan(repo_id: str, current_relative_paths: list[str]) -> None:
    normalized_paths = [normalize_repo_path(path) for path in current_relative_paths if normalize_repo_path(path)]
    with db_cursor() as (_conn, cursor):
        if normalized_paths:
            placeholders = ", ".join("?" for _ in normalized_paths)
            cursor.execute(
                f"""
                DELETE FROM repo_files
                WHERE repo_id = ? AND relative_path NOT IN ({placeholders})
                """,
                (repo_id, *normalized_paths),
            )
            return
        cursor.execute("DELETE FROM repo_files WHERE repo_id = ?", (repo_id,))


def upsert_code_block(block: CodeBlock) -> dict:
    block_id = block.id or uuid.uuid4().hex
    now = _now()
    metadata_json = json.dumps(block.metadata or {}, sort_keys=True)
    with db_cursor() as (_conn, cursor):
        row = cursor.execute("SELECT id, created_at FROM code_blocks WHERE id = ?", (block_id,)).fetchone()
        if row:
            created_at = row["created_at"]
            cursor.execute(
                """
                UPDATE code_blocks
                SET repo_id = ?, file_id = ?, relative_path = ?, language = ?, block_type = ?,
                    name = ?, qualified_name = ?, parent_block_id = ?, parent_symbol = ?,
                    start_line = ?, end_line = ?, signature = ?, content = ?, code_hash = ?,
                    metadata_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    block.repo_id,
                    block.file_id,
                    block.relative_path,
                    block.language,
                    block.block_type,
                    block.name,
                    block.qualified_name,
                    block.parent_block_id,
                    block.parent_symbol,
                    block.start_line,
                    block.end_line,
                    block.signature,
                    block.content,
                    block.code_hash,
                    metadata_json,
                    now,
                    block_id,
                ),
            )
        else:
            created_at = now
            cursor.execute(
                """
                INSERT INTO code_blocks (
                    id, repo_id, file_id, relative_path, language, block_type, name,
                    qualified_name, parent_block_id, parent_symbol, start_line, end_line,
                    signature, content, code_hash, metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    block_id,
                    block.repo_id,
                    block.file_id,
                    block.relative_path,
                    block.language,
                    block.block_type,
                    block.name,
                    block.qualified_name,
                    block.parent_block_id,
                    block.parent_symbol,
                    block.start_line,
                    block.end_line,
                    block.signature,
                    block.content,
                    block.code_hash,
                    metadata_json,
                    created_at,
                    now,
                ),
            )
    return get_block(block_id)


def get_files_for_repo(repo_id: str) -> list[dict]:
    with db_cursor() as (_conn, cursor):
        rows = cursor.execute(
            """
            SELECT
                f.*,
                COUNT(b.id) AS block_count
            FROM repo_files f
            LEFT JOIN code_blocks b ON b.file_id = f.id
            WHERE f.repo_id = ?
            GROUP BY f.id
            ORDER BY f.relative_path
            """,
            (repo_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_blocks_for_file(repo_id: str, relative_path: str) -> list[dict]:
    normalized_path = normalize_repo_path(relative_path)
    with db_cursor() as (_conn, cursor):
        rows = cursor.execute(
            """
            SELECT b.*
            FROM code_blocks b
            JOIN repo_files f ON f.id = b.file_id
            WHERE b.repo_id = ? AND f.relative_path = ?
            ORDER BY b.start_line, b.end_line, b.name
            """,
            (repo_id, normalized_path),
        ).fetchall()
    return [_deserialize_block(row) for row in rows]


def get_block(block_id: str) -> dict | None:
    with db_cursor() as (_conn, cursor):
        row = cursor.execute("SELECT * FROM code_blocks WHERE id = ?", (block_id,)).fetchone()
    return _deserialize_block(row) if row else None


def _deserialize_block(row) -> dict:
    payload = dict(row)
    payload["metadata"] = json.loads(payload.pop("metadata_json") or "{}")
    return payload
