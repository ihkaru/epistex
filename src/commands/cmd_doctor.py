"""Health check engine inspecting schema, dead links, line limits, and secret leaks."""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
from config.app import ROOT_DIR, KNOWLEDGE_DIR, EX_OK, EX_DATAERR
from src.contracts.events import EventDispatcherInterface
from src.core.scanner import scan_markdown_files, build_inverted_file_index
from src.core.io_stream import read_frontmatter_streaming
from src.core.schema_validator import SchemaValidator
from src.events.domain_events import HealthCheckCompletedEvent

LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
SECRET_PATTERNS = [
    re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----"),
    re.compile(r"(?:infisical|secret|password|bearer)[\s:=]+['\"][a-zA-Z0-9_\-]{20,}['\"]", re.IGNORECASE),
]


def _check_links(path: Path, index: Set[str]) -> List[Dict[str, Any]]:
    """Verify relative markdown links against inverted index in O(1) per link."""
    issues = []
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        for match in LINK_PATTERN.finditer(content):
            target = match.group(2).strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean_target = target.split("#")[0].split("?")[0]
            if not clean_target:
                continue
            resolved = (path.parent / clean_target).resolve()
            try:
                rel = resolved.relative_to(ROOT_DIR.resolve()).as_posix()
                if rel not in index:
                    issues.append({"file": str(path), "link": target, "error": "Dead link reference"})
            except ValueError:
                issues.append({"file": str(path), "link": target, "error": "Link points outside repository"})
    except OSError:
        pass
    return issues


def _check_secret_leaks(path: Path) -> List[Dict[str, Any]]:
    """Scan file content for accidentally committed API keys or private tokens."""
    issues = []
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        for idx, line in enumerate(content.splitlines(), start=1):
            for pat in SECRET_PATTERNS:
                if pat.search(line):
                    issues.append({"file": str(path), "line": idx, "error": "Potential secret credential leak"})
    except OSError:
        pass
    return issues


def run_doctor(
    base_dir: Path = KNOWLEDGE_DIR,
    dispatcher: EventDispatcherInterface | None = None,
) -> Tuple[int, Dict[str, Any]]:
    """Execute complete health audit: schema linting, dead links, and secret leaks."""
    validator = SchemaValidator()
    file_index = build_inverted_file_index(ROOT_DIR)
    schema_issues = []
    link_issues = []
    leak_issues = []
    total_files = 0

    for doc in scan_markdown_files(base_dir):
        total_files += 1
        frontmatter, end_line, _ = read_frontmatter_streaming(doc)
        issues = validator.validate_document(doc, frontmatter, end_line)
        for issue in issues:
            schema_issues.append({
                "file": str(issue.file),
                "line": issue.line,
                "field": issue.field_name,
                "error_type": issue.error_type,
                "message": issue.message,
                "fix_hint": issue.fix_hint,
            })
        link_issues.extend(_check_links(doc, file_index))
        leak_issues.extend(_check_secret_leaks(doc))

    total_problems = len(schema_issues) + len(link_issues) + len(leak_issues)
    exit_code = EX_OK if total_problems == 0 else EX_DATAERR

    if dispatcher:
        dispatcher.dispatch(HealthCheckCompletedEvent(total_files, total_problems, len(link_issues)))

    result = {
        "status": "ok" if exit_code == EX_OK else "error",
        "exit_code": exit_code,
        "scanned_files": total_files,
        "total_issues": total_problems,
        "schema_issues": schema_issues,
        "dead_links": link_issues,
        "secret_leaks": leak_issues,
    }
    return exit_code, result
