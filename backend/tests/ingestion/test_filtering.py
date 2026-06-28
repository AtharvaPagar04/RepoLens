from app.ingestion.filtering import filter_files
from app.models.repo_file import RepoFileRecord


def make_file(relative_path: str, size_bytes: int = 100) -> RepoFileRecord:
    extension = ""
    if "." in relative_path.rsplit("/", 1)[-1]:
        extension = "." + relative_path.rsplit(".", 1)[-1]
    return RepoFileRecord(
        path=f"/fake/repo/{relative_path}",
        relative_path=relative_path,
        extension=extension,
        size_bytes=size_bytes,
    )


def test_filtering_skips_common_noise(tmp_path):
    files = [
        make_file("src/app.py"),
        make_file("node_modules/react/index.js"),
        make_file(".git/config"),
        make_file("dist/app.min.js"),
        make_file(".repolens_ingestion_state.json"),
    ]

    filtered = filter_files(files, str(tmp_path))
    paths = {file.relative_path for file in filtered}

    assert "src/app.py" in paths
    assert "node_modules/react/index.js" not in paths
    assert ".git/config" not in paths
    assert "dist/app.min.js" not in paths
    assert ".repolens_ingestion_state.json" not in paths

