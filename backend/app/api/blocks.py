"""Block detail endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.db.repositories import get_block

router = APIRouter(prefix="/api/blocks", tags=["blocks"])


@router.get("/{block_id}")
async def get_block_detail(block_id: str) -> dict:
    block = get_block(block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return {
        "id": block["id"],
        "repo_id": block["repo_id"],
        "file_id": block["file_id"],
        "relative_path": block["relative_path"],
        "name": block["name"],
        "qualified_name": block["qualified_name"],
        "block_type": block["block_type"],
        "language": block["language"],
        "start_line": block["start_line"],
        "end_line": block["end_line"],
        "signature": block["signature"],
        "content": block["content"],
        "code_hash": block["code_hash"],
        "metadata": block["metadata"],
    }
