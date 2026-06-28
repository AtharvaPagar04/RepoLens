from app.ingestion.language import detect_languages
from app.models.repo_file import RepoFileRecord


def test_language_detection_identifies_common_languages():
    files = [
        RepoFileRecord(path="/tmp/a.py", relative_path="a.py", extension=".py", size_bytes=1),
        RepoFileRecord(path="/tmp/b.js", relative_path="b.js", extension=".js", size_bytes=1),
        RepoFileRecord(path="/tmp/c.ts", relative_path="c.ts", extension=".ts", size_bytes=1),
        RepoFileRecord(path="/tmp/d.tsx", relative_path="d.tsx", extension=".tsx", size_bytes=1),
    ]

    detect_languages(files)

    assert [file.language for file in files] == [
        "python",
        "javascript",
        "typescript",
        "typescript",
    ]

