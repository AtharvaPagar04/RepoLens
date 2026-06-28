from pathlib import Path

from app.ingestion.block_extractor import extract_code_blocks
from app.ingestion.parser import parse_file
from app.models.repo_file import RepoFileRecord


def test_parser_extracts_python_function_and_class_method(tmp_path: Path):
    path = tmp_path / "main.py"
    path.write_text(
        "def top_level(a, b):\n"
        "    return a + b\n\n"
        "class Greeter:\n"
        "    def hello(self, name):\n"
        "        return name\n",
        encoding="utf-8",
    )
    file = RepoFileRecord(
        path=str(path),
        relative_path="main.py",
        extension=".py",
        size_bytes=path.stat().st_size,
        language="python",
    )

    parsed = parse_file(file)
    blocks = extract_code_blocks(parsed, file)
    names = {(block.name, block.block_type) for block in blocks}

    assert ("top_level", "function") in names
    assert ("Greeter", "class") in names
    assert ("hello", "method") in names
    top_level = next(block for block in blocks if block.name == "top_level")
    assert top_level.start_line == 1
    assert top_level.end_line == 2
    assert top_level.content.startswith("def top_level")
    assert top_level.code_hash


def test_parser_extracts_python_nested_class_and_async_function(tmp_path: Path):
    path = tmp_path / "nested.py"
    path.write_text(
        "class Outer:\n"
        "    class Inner:\n"
        "        def ping(self):\n"
        "            return 'pong'\n\n"
        "async def fetch_data(value):\n"
        "    return value\n",
        encoding="utf-8",
    )
    file = RepoFileRecord(
        path=str(path),
        relative_path="nested.py",
        extension=".py",
        size_bytes=path.stat().st_size,
        language="python",
    )

    parsed = parse_file(file)
    blocks = extract_code_blocks(parsed, file)

    assert any(block.name == "Outer" and block.block_type == "class" for block in blocks)
    assert any(
        block.name == "Inner"
        and block.block_type == "class"
        and block.qualified_name == "Outer.Inner"
        for block in blocks
    )
    assert any(
        block.name == "ping"
        and block.block_type == "method"
        and block.qualified_name == "Outer.Inner.ping"
        for block in blocks
    )
    assert any(block.name == "fetch_data" and block.block_type == "function" for block in blocks)


def test_parser_extracts_js_function_arrow_and_tsx_component_hook(tmp_path: Path):
    js_path = tmp_path / "utils.js"
    js_path.write_text(
        "function greet(name) {\n"
        "  return name;\n"
        "}\n"
        "const add = (a, b) => a + b;\n",
        encoding="utf-8",
    )
    js_file = RepoFileRecord(
        path=str(js_path),
        relative_path="utils.js",
        extension=".js",
        size_bytes=js_path.stat().st_size,
        language="javascript",
    )
    js_parsed = parse_file(js_file)
    js_blocks = extract_code_blocks(js_parsed, js_file)
    assert any(block.name == "greet" and block.block_type == "function" for block in js_blocks)
    assert any(block.name == "add" and block.block_type == "function" for block in js_blocks)

    tsx_path = tmp_path / "App.tsx"
    tsx_path.write_text(
        "const useThing = () => {\n"
        "  return 1;\n"
        "};\n"
        "const App = () => {\n"
        "  return <div>Hello</div>;\n"
        "};\n",
        encoding="utf-8",
    )
    tsx_file = RepoFileRecord(
        path=str(tsx_path),
        relative_path="App.tsx",
        extension=".tsx",
        size_bytes=tsx_path.stat().st_size,
        language="typescript",
    )
    tsx_parsed = parse_file(tsx_file)
    tsx_blocks = extract_code_blocks(tsx_parsed, tsx_file)

    assert any(block.name == "useThing" and block.block_type == "hook" for block in tsx_blocks)
    assert any(block.name == "App" and block.block_type == "component" for block in tsx_blocks)


def test_parser_handles_broken_python_without_crashing(tmp_path: Path):
    path = tmp_path / "broken.py"
    path.write_text(
        "def broken(\n"
        "    return 1\n",
        encoding="utf-8",
    )
    file = RepoFileRecord(
        path=str(path),
        relative_path="broken.py",
        extension=".py",
        size_bytes=path.stat().st_size,
        language="python",
    )

    parsed = parse_file(file)
    blocks = extract_code_blocks(parsed, file)

    assert parsed.parse_status in {"ok", "failed"}
    assert isinstance(blocks, list)
