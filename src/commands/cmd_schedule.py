"""Heap-based priority queue for querying upcoming deadlines in O(M log k) time."""

import heapq
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from config.app import KNOWLEDGE_DIR, EX_OK
from src.core.scanner import scan_markdown_files
from src.core.io_stream import read_frontmatter_streaming


def _extract_doc_deadlines(doc: Path, meta: Dict[str, Any]) -> List[Tuple[str, str, str, str]]:
    """Extract (due_date, milestone, doc_title, doc_path) entries from frontmatter."""
    items: List[Tuple[str, str, str, str]] = []
    deadlines = meta.get("deadlines", [])
    if isinstance(deadlines, list):
        for dl in deadlines:
            if isinstance(dl, dict) and "due" in dl:
                due = str(dl.get("due", ""))
                milestone = str(dl.get("milestone", "Untitled Milestone"))
                title = str(meta.get("title", doc.stem))
                items.append((due, milestone, title, str(doc)))
    return items


def run_schedule(
    base_dir: Path = KNOWLEDGE_DIR,
    limit: int = 10,
    category: Optional[str] = None,
    active_only: bool = True,
) -> Tuple[int, Dict[str, Any]]:
    """Query upcoming schedules using bounded min-heap in O(M log k) time."""
    # Min-heap items: (due_date, milestone, title, path)
    heap: List[Tuple[str, str, str, str]] = []

    for doc in scan_markdown_files(base_dir):
        meta, _, _ = read_frontmatter_streaming(doc)
        if active_only and meta.get("status") not in ("active", "draft", "review"):
            continue
        if category and meta.get("category") != category:
            continue

        for item in _extract_doc_deadlines(doc, meta):
            heapq.heappush(heap, item)

    results: List[Dict[str, Any]] = []
    while heap and len(results) < limit:
        due, milestone, title, path = heapq.heappop(heap)
        results.append({
            "due": due,
            "milestone": milestone,
            "document": title,
            "path": path,
        })

    payload = {
        "status": "ok",
        "exit_code": EX_OK,
        "total_scheduled": len(results),
        "limit": limit,
        "schedules": results,
    }
    return EX_OK, payload
