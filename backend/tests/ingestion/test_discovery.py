from pathlib import Path

from app.ingestion.discovery import discover_files


def test_discovery_returns_relative_paths(tmp_path: Path):
    (tmp_path / "backend").mkdir()
    file_path = tmp_path / "backend" / "main.py"
    file_path.write_text("print('hi')\n", encoding="utf-8")

    files = discover_files(str(tmp_path))

    assert len(files) == 1
    assert files[0].relative_path == "backend/main.py"
    assert files[0].path == str(file_path.resolve())

