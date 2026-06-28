"""Convert parsed symbols into strict CodeBlock records."""

from __future__ import annotations

from app.ingestion.hashing import hash_content
from app.models.code_block import CodeBlock
from app.models.parsed import ParsedFile
from app.models.repo_file import RepoFileRecord


def extract_code_blocks(parsed: ParsedFile, file: RepoFileRecord) -> list[CodeBlock]:
    """Create strict code blocks from parsed symbols."""
    if parsed.parse_status == "failed":
        return []

    blocks: list[CodeBlock] = []
    for symbol in parsed.symbols:
        block_type = _classify_block_type(symbol.name, symbol.symbol_type, file.language)
        content = symbol.content or ""
        blocks.append(
            CodeBlock(
                file_path=file.path,
                relative_path=file.relative_path,
                language=file.language,
                block_type=block_type,
                name=symbol.name,
                qualified_name=symbol.qualified_name,
                parent_symbol=symbol.parent_symbol,
                start_line=symbol.start_line,
                end_line=symbol.end_line,
                signature=symbol.signature,
                content=content,
                code_hash=hash_content(content),
                metadata={
                    "imports": symbol.imports,
                    "calls": symbol.calls,
                    "parameters": symbol.parameters,
                    "methods": symbol.methods,
                    "docstring": symbol.docstring,
                    "source_symbol_type": symbol.symbol_type,
                },
            )
        )
    return blocks


def _classify_block_type(name: str, symbol_type: str, language: str) -> str:
    if symbol_type == "class":
        return "class"
    if symbol_type == "method":
        return "method"
    if language in {"javascript", "typescript"}:
        if _is_hook(name):
            return "hook"
        if _is_component(name):
            return "component"
    return "function"


def _is_component(name: str) -> bool:
    return bool(name) and name[:1].isupper()


def _is_hook(name: str) -> bool:
    return bool(name) and name.startswith("use") and len(name) > 3 and name[3:4].isupper()

