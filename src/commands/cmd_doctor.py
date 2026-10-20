"""Health check engine inspecting schema, dead links, line limits, and secret leaks."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from config.app import ROOT_DIR, KNOWLEDGE_DIR, EX_OK, EX_DATAERR
from src.contracts.asset_storage import AssetStorageInterface
from src.contracts.events import EventDispatcherInterface
from src.core.companion import parse_companion_metadata
from src.core.scanner import scan_markdown_files, build_inverted_file_index
from src.core.io_stream import read_frontmatter_streaming
from src.core.schema_validator import SchemaValidator
from src.events.domain_events import HealthCheckCompletedEvent
from src.providers.storage.factory import create_asset_storage

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


def _check_companion_assets(doc: Path, meta: Dict[str, Any], storage: Any) -> List[Dict[str, Any]]:
    """Verify cloud asset existence referenced in companion documents on-demand."""
    issues = []
    asset_info = parse_companion_metadata(meta)
    if asset_info and storage:
        key = asset_info.get("remote_key", "")
        if key and not storage.exists(key):
            issues.append({
                "file": str(doc),
                "remote_key": key,
                "error": "Asset missing from storage backend",
                "fix_hint": f"Run 'gx asset push <file> --key {key}' to upload.",
            })
    return issues


def _audit_single_document(
    doc: Path,
    validator: SchemaValidator,
    file_index: Set[str],
    storage: Optional[AssetStorageInterface],
    check_assets: bool,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Execute schema, link, secret, and asset audits for a single document."""
    frontmatter, end_line, _ = read_frontmatter_streaming(doc)
    schema_errs = [
        {
            "file": str(issue.file),
            "line": issue.line,
            "field": issue.field_name,
            "error_type": issue.error_type,
            "message": issue.message,
            "fix_hint": issue.fix_hint,
        }
        for issue in validator.validate_document(doc, frontmatter, end_line)
    ]
    link_errs = _check_links(doc, file_index)
    leak_errs = _check_secret_leaks(doc)
    asset_errs = _check_companion_assets(doc, frontmatter, storage) if check_assets else []
    return schema_errs, link_errs, leak_errs, asset_errs


def run_doctor(
    base_dir: Path = KNOWLEDGE_DIR,
    dispatcher: Optional[EventDispatcherInterface] = None,
    check_assets: bool = False,
    cloud_auth: Optional[str] = None,
    secret_provider: Optional[SecretProviderInterface] = None,
    asset_storage: Optional[AssetStorageInterface] = None,
) -> Tuple[int, Dict[str, Any]]:
    """Execute complete health audit: schema linting, dead links, secret leaks, and opt-in asset checks."""
    validator = SchemaValidator()
    file_index = build_inverted_file_index(ROOT_DIR)
    storage = (asset_storage or create_asset_storage(auth_mode=cloud_auth, secret_provider=secret_provider)) if check_assets else None
    schema_issues, link_issues, leak_issues, asset_issues = [], [], [], []
    total_files = 0


    for doc in scan_markdown_files(base_dir):
        total_files += 1
        s_errs, l_errs, k_errs, a_errs = _audit_single_document(doc, validator, file_index, storage, check_assets)
        schema_issues.extend(s_errs)
        link_issues.extend(l_errs)
        leak_issues.extend(k_errs)
        asset_issues.extend(a_errs)

    total_problems = len(schema_issues) + len(link_issues) + len(leak_issues) + len(asset_issues)
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
        "asset_issues": asset_issues,
    }
    return exit_code, result
