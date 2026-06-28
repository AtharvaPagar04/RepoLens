"""SQLite schema for RepoLens Phase 1."""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS repos (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_url TEXT,
    local_path TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS repo_files (
    id TEXT PRIMARY KEY,
    repo_id TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    absolute_path TEXT NOT NULL,
    language TEXT,
    extension TEXT,
    size_bytes INTEGER,
    content_hash TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(repo_id, relative_path),
    FOREIGN KEY(repo_id) REFERENCES repos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS code_blocks (
    id TEXT PRIMARY KEY,
    repo_id TEXT NOT NULL,
    file_id TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    language TEXT,
    block_type TEXT NOT NULL,
    name TEXT NOT NULL,
    qualified_name TEXT,
    parent_block_id TEXT,
    parent_symbol TEXT,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    signature TEXT,
    content TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(repo_id) REFERENCES repos(id) ON DELETE CASCADE,
    FOREIGN KEY(file_id) REFERENCES repo_files(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_repo_files_repo_path
    ON repo_files(repo_id, relative_path);

CREATE INDEX IF NOT EXISTS idx_code_blocks_file
    ON code_blocks(file_id, start_line);

CREATE INDEX IF NOT EXISTS idx_code_blocks_repo_path
    ON code_blocks(repo_id, relative_path);
"""

