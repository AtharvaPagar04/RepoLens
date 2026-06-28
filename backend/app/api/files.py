"""File tree and block listing endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.db.repositories import get_blocks_for_file, get_files_for_repo, get_repo

router = APIRouter(prefix="/api/repos", tags=["files"])


@router.get("/{repo_id}/files/tree")
async def get_file_tree(repo_id: str) -> dict:
    repo = get_repo(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    files = get_files_for_repo(repo_id)
    return {"repo_id": repo_id, "tree": _build_tree(files)}


@router.get("/{repo_id}/files/blocks")
async def get_file_blocks(repo_id: str, path: str = Query(...)) -> dict:
    repo = get_repo(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    blocks = get_blocks_for_file(repo_id, path)
    if not blocks:
        file_paths = {item["relative_path"] for item in get_files_for_repo(repo_id)}
        if path not in file_paths:
            raise HTTPException(status_code=404, detail="File not found in repo")
    return {
        "repo_id": repo_id,
        "path": path,
        "blocks": [
            {
                "id": block["id"],
                "name": block["name"],
                "qualified_name": block["qualified_name"],
                "block_type": block["block_type"],
                "language": block["language"],
                "start_line": block["start_line"],
                "end_line": block["end_line"],
                "signature": block["signature"],
                "code_hash": block["code_hash"],
            }
            for block in blocks
        ],
    }


def _build_tree(files: list[dict]) -> list[dict]:
    root: dict[str, dict] = {}
    for item in files:
        parts = item["relative_path"].split("/")
        current = root
        current_path = []
        for directory in parts[:-1]:
            current_path.append(directory)
            current = current.setdefault(
                directory,
                {
                    "name": directory,
                    "path": "/".join(current_path),
                    "type": "directory",
                    "children": {},
                },
            )["children"]
        filename = parts[-1]
        file_path = item["relative_path"]
        current[filename] = {
            "name": filename,
            "path": file_path,
            "type": "file",
            "language": item["language"],
            "has_blocks": int(item["block_count"] or 0) > 0,
            "block_count": int(item["block_count"] or 0),
        }
    return _serialize_tree(root)


def _serialize_tree(node: dict[str, dict]) -> list[dict]:
    output: list[dict] = []
    for key in sorted(node):
        item = node[key]
        if item["type"] == "directory":
            output.append(
                {
                    "name": item["name"],
                    "path": item["path"],
                    "type": "directory",
                    "children": _serialize_tree(item["children"]),
                }
            )
        else:
            output.append(item)
    return output
