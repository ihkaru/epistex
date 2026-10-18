"""Pruned fast filesystem traversal and inverted index generator."""

import os
from pathlib import Path
from typing import Generator, Optional, Set
from config.app import DEFAULT_IGNORED_DIRS


def scan_markdown_files(
    base_path: Path, ignored_dirs: Optional[Set[str]] = None
) -> Generator[Path, None, None]:
    """Efficiently yield markdown file paths using pruned os.scandir() traversal in O(V) time."""
    ignored = ignored_dirs if ignored_dirs is not None else DEFAULT_IGNORED_DIRS
    try:
        with os.scandir(base_path) as it:
            for entry in it:
                if entry.is_dir(follow_symlinks=False):
                    if entry.name not in ignored and not entry.name.startswith("."):
                        yield from scan_markdown_files(Path(entry.path), ignored)
                elif entry.is_file(follow_symlinks=False) and entry.name.endswith(".md"):
                    yield Path(entry.path)
    except PermissionError:
        return


def build_inverted_file_index(
    base_path: Path, ignored_dirs: Optional[Set[str]] = None
) -> Set[str]:
    """Single-pass O(N) hash inverted index of all relative file paths in repository."""
    ignored = ignored_dirs if ignored_dirs is not None else DEFAULT_IGNORED_DIRS
    resolved_base = base_path.resolve()
    indexed_files: Set[str] = set()

    def _walk_and_index(current_dir: Path) -> None:
        try:
            with os.scandir(current_dir) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        if entry.name not in ignored and not entry.name.startswith("."):
                            _walk_and_index(Path(entry.path))
                    elif entry.is_file(follow_symlinks=False):
                        rel = Path(entry.path).resolve().relative_to(resolved_base).as_posix()
                        indexed_files.add(rel)
        except PermissionError:
            return

    _walk_and_index(resolved_base)
    return indexed_files
