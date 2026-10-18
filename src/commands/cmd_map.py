"""Token-budget bounded repository layout and domain overview generator."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from config.app import KNOWLEDGE_DIR, DEFAULT_IGNORED_DIRS, EX_OK
from src.core.io_stream import read_frontmatter_streaming


def _build_tree(
    current_path: Path, current_depth: int, max_depth: int, compact: bool
) -> Dict[str, Any]:
    """Recursively build bounded directory tree up to max_depth in O(V) time."""
    node: Dict[str, Any] = {
        "name": current_path.name,
        "type": "directory" if current_path.is_dir() else "file",
        "path": str(current_path),
    }

    if current_path.is_file():
        if current_path.name.endswith(".md"):
            meta, _, _ = read_frontmatter_streaming(current_path)
            node["title"] = meta.get("title", current_path.stem)
            node["status"] = meta.get("status", "unknown")
            node["category"] = meta.get("category", "document")
        return node

    if current_depth >= max_depth:
        # Bounded leaf: summarize child counts instead of full recursion
        doc_count = sum(1 for p in current_path.glob("*.md"))
        node["bounded"] = True
        node["document_count"] = doc_count
        return node

    children: List[Dict[str, Any]] = []
    try:
        with os.scandir(current_path) as it:
            for entry in sorted(it, key=lambda e: e.name):
                if entry.name in DEFAULT_IGNORED_DIRS or entry.name.startswith("."):
                    continue
                child_path = Path(entry.path)
                if entry.is_dir(follow_symlinks=False) or entry.name.endswith(".md"):
                    child_node = _build_tree(child_path, current_depth + 1, max_depth, compact)
                    children.append(child_node)
    except PermissionError:
        pass

    node["children"] = children
    return node


def run_map(
    base_dir: Path = KNOWLEDGE_DIR, depth: int = 2, compact: bool = False
) -> Tuple[int, Dict[str, Any]]:
    """Generate token-efficient structural map of knowledge base."""
    tree = _build_tree(base_dir, current_depth=0, max_depth=depth, compact=compact)
    payload = {
        "status": "ok",
        "exit_code": EX_OK,
        "root": str(base_dir),
        "max_depth": depth,
        "compact": compact,
        "tree": tree,
    }
    return EX_OK, payload
