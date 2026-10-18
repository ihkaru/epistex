"""Knowledge base core algorithmic engine and filesystem primitives."""

from .errors import (
    KBError,
    UsageError,
    ValidationError,
    FileNotFoundKBError,
    RunnerError,
    VaultError,
)
from .yaml_parser import parse_restricted_yaml
from .io_stream import read_frontmatter_streaming, atomic_write_text
from .scanner import scan_markdown_files, build_inverted_file_index
from .schema_validator import SchemaValidator

__all__ = [
    "KBError",
    "UsageError",
    "ValidationError",
    "FileNotFoundKBError",
    "RunnerError",
    "VaultError",
    "parse_restricted_yaml",
    "read_frontmatter_streaming",
    "atomic_write_text",
    "scan_markdown_files",
    "build_inverted_file_index",
    "SchemaValidator",
]
