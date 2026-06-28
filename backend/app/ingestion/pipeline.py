"""Phase 1 indexing pipeline for RepoLens."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from app.db.repositories import (
    create_repo,
    delete_blocks_for_file,
    delete_repo_files_missing_from_scan,
    upsert_code_block,
    upsert_repo_file,
)
from app.ingestion.block_extractor import extract_code_blocks
from app.ingestion.discovery import discover_files
from app.ingestion.filtering import filter_files
from app.ingestion.hashing import hash_file
from app.ingestion.language import detect_languages
from app.ingestion.loader import load_github_repository, load_local_repository
from app.ingestion.parser import parse_file


@dataclass
class PipelineStats:
    files_discovered: int = 0
    files_indexed: int = 0
    files_skipped: int = 0
    blocks_extracted: int = 0
    parse_errors: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def index_local_repository(path: str, name: str | None = None) -> dict:
    repository = load_local_repository(path, name=name)
    return _index_repository(repository)


def index_github_repository(repo_url: str, name: str | None = None) -> dict:
    repository = load_github_repository(repo_url, name=name)
    return _index_repository(repository)


def _index_repository(repository: dict) -> dict:
    stats = PipelineStats()

    repo_row = create_repo(
        name=repository["repository_name"],
        local_path=repository["repository_root"],
        source_url=repository.get("source_url"),
    )

    discovered_files = discover_files(repository["repository_root"])
    stats.files_discovered = len(discovered_files)

    filtered_files = filter_files(discovered_files, repository["repository_root"])
    detect_languages(filtered_files)
    delete_repo_files_missing_from_scan(
        repo_row["id"],
        [file.relative_path for file in filtered_files],
    )

    for file in filtered_files:
        if file.skipped:
            stats.files_skipped += 1
            continue

        parsed = parse_file(file)
        if parsed.parse_status == "failed":
            stats.parse_errors += 1

        content_hash = hash_file(file.path)
        file_row = upsert_repo_file(
            repo_id=repo_row["id"],
            relative_path=file.relative_path,
            absolute_path=file.path,
            language=file.language,
            extension=file.extension,
            size_bytes=file.size_bytes,
            content_hash=content_hash,
        )

        delete_blocks_for_file(file_row["id"])
        blocks = extract_code_blocks(parsed, file)
        for block in blocks:
            block.repo_id = repo_row["id"]
            block.file_id = file_row["id"]
            upsert_code_block(block)
        stats.blocks_extracted += len(blocks)
        stats.files_indexed += 1

    stats.files_skipped += stats.files_discovered - len(filtered_files)

    return {"repo": repo_row, "stats": stats.to_dict()}
