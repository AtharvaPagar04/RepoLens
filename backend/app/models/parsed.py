"""Parsed AST output models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ParsedSymbol:
    """A symbol extracted from a source file."""

    name: str
    qualified_name: str
    symbol_type: str
    parent_symbol: str
    start_line: int
    end_line: int
    signature: str = ""
    content: str = ""
    imports: list[str] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)
    parameters: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    docstring: str = ""


@dataclass
class ParsedFile:
    """Parser output for one source file."""

    relative_path: str
    language: str
    parse_status: str
    content: str = ""
    imports: list[str] = field(default_factory=list)
    symbols: list[ParsedSymbol] = field(default_factory=list)

