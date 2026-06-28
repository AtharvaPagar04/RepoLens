# RepoLens

Phase 1 backend scaffold for repository indexing and code block inspection.

## Backend V1 Scope

- Local repository indexing
- GitHub repository import and indexing
- File discovery and filtering
- Language detection
- Tree-sitter parsing
- Strict `CodeBlock` extraction
- SQLite-backed persistence
- Safe same-repo reindexing
- Repo, file tree, file blocks, and block detail APIs

## Setup

```bash
cd ~/RepoLens
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run Tests

```bash
cd ~/RepoLens
PYTHONPATH=backend .venv/bin/python -m pytest backend/tests -q
```

## Run Server (Backend & Frontend)

```bash
# backend
cd ~/RepoLens
PYTHONPATH=backend .venv/bin/uvicorn app.main:app --reload

# frontend
cd ~/RepoLens/frontend
npm install
npm run dev
```

## Available Endpoints

- `GET /health`
- `POST /api/repos/index-local`
- `POST /api/repos/import-github`
- `GET /api/repos`
- `GET /api/repos/{repo_id}`
- `POST /api/repos/{repo_id}/reindex`
- `DELETE /api/repos/{repo_id}`
- `GET /api/repos/{repo_id}/files/tree`
- `GET /api/repos/{repo_id}/files/blocks?path=<relative_path>`
- `GET /api/blocks/{block_id}`

## Compile Check

```bash
cd ~/RepoLens
.venv/bin/python -m compileall backend/app backend/tests
```

## Current Limitations

- GitHub import is synchronous in V1.
- Existing local clones are reused as-is; V1 does not fetch or pull updates yet.
- Private GitHub repositories are not supported yet.
- LLM summaries are not implemented.
- Embeddings and vector search are not implemented.
- Caller/callee graph traversal is not implemented.
- Parser coverage is best-effort for JS, TS, and TSX.
