"""CodeBlock model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CodeBlock:
    id: str = ""
    repo_id: str = ""
    file_id: str = ""
    file_path: str = ""
    relative_path: str = ""
    language: str = ""
    block_type: str = ""
    name: str = ""
    qualified_name: str = ""
    parent_block_id: str | None = None
    parent_symbol: str = ""
    start_line: int = 0
    end_line: int = 0
    signature: str = ""
    content: str = ""
    code_hash: str = ""
    metadata: dict[str, object] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""

