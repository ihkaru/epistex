"""Deterministic release readiness detector and SemVer bump recommendation engine."""

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config.app import APP_VERSION

CODE_DIRECTORIES = {"src", "bin", "config"}
CODE_FILES = {"pyproject.toml"}


def _run_git_cmd(args: List[str], cwd: Path) -> Optional[str]:
    """Execute git command safely returning stripped stdout or None on failure."""
    try:
        proc = subprocess.run(
            ["git"] + args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=5.0,
        )
        return proc.stdout.strip() if proc.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _get_latest_git_tag(root_dir: Path) -> Optional[str]:
    """Retrieve the latest annotated or lightweight git tag."""
    return _run_git_cmd(["describe", "--tags", "--abbrev=0"], root_dir)


def _get_unreleased_commits(root_dir: Path, latest_tag: str) -> List[Dict[str, str]]:
    """Get list of commit hashes and subject lines since latest tag."""
    output = _run_git_cmd(["log", f"{latest_tag}..HEAD", "--oneline"], root_dir)
    if not output:
        return []

    commits = []
    for line in output.splitlines():
        parts = line.strip().split(" ", 1)
        if len(parts) == 2:
            commits.append({"hash": parts[0], "message": parts[1]})
        elif len(parts) == 1 and parts[0]:
            commits.append({"hash": parts[0], "message": ""})
    return commits


def _has_code_modifications(root_dir: Path, latest_tag: str) -> Tuple[bool, bool]:
    """Check if unreleased diff touches engine code versus content-only documents."""
    diff_output = _run_git_cmd(["diff", "--name-only", f"{latest_tag}..HEAD"], root_dir)
    if not diff_output:
        return False, False

    changed_files = [line.strip() for line in diff_output.splitlines() if line.strip()]
    code_touched = False
    content_touched = False

    for file_path in changed_files:
        top_segment = file_path.split("/")[0]
        if top_segment in CODE_DIRECTORIES or file_path in CODE_FILES:
            code_touched = True
        elif top_segment == "knowledge":
            content_touched = True

    return code_touched, content_touched


def _determine_bump_type(commits: List[Dict[str, str]]) -> str:
    """Analyze commit messages to determine SemVer bump (patch, minor, major)."""
    for commit in commits:
        msg = commit.get("message", "")
        if "BREAKING CHANGE" in msg or re.search(r"^[a-z]+!:", msg):
            return "major"

    for commit in commits:
        msg = commit.get("message", "")
        if re.search(r"^feat(?:\([^\)]+\))?:", msg):
            return "minor"

    return "patch"


def _evaluate_unreleased_diff(
    root_dir: Path, latest_tag: str, commits: List[Dict[str, str]]
) -> Dict[str, Any]:
    """Evaluate unreleased commits to distinguish code changes from content-only edits."""
    code_touched, content_touched = _has_code_modifications(root_dir, latest_tag)
    if not code_touched:
        return {
            "release_required": False,
            "mode": "upstream_starter_kit",
            "current_version": APP_VERSION,
            "latest_tag": latest_tag,
            "unreleased_commits_count": len(commits),
            "recommended_bump": None,
            "code_changes_detected": False,
            "content_only_changes": content_touched,
            "reason": "Unreleased commits are content-only (knowledge documents). Engine release not required.",
            "unreleased_commits": commits,
        }

    bump_type = _determine_bump_type(commits)
    return {
        "release_required": True,
        "mode": "upstream_starter_kit",
        "current_version": APP_VERSION,
        "latest_tag": latest_tag,
        "unreleased_commits_count": len(commits),
        "recommended_bump": bump_type,
        "code_changes_detected": True,
        "content_only_changes": content_touched,
        "reason": f"Detected {len(commits)} unreleased commit(s) touching engine code since {latest_tag}.",
        "unreleased_commits": commits,
    }


def audit_release_readiness(root_dir: Path, is_starter_kit: bool = True) -> Dict[str, Any]:
    """Audit repository status to determine if a new engine release is required."""
    if not is_starter_kit:
        return {
            "release_required": False,
            "mode": "downstream_operational",
            "current_version": APP_VERSION,
            "latest_tag": None,
            "unreleased_commits_count": 0,
            "recommended_bump": None,
            "code_changes_detected": False,
            "content_only_changes": False,
            "reason": "Downstream operational mode: engine release checks suppressed to prevent prompt poisoning.",
            "unreleased_commits": [],
        }

    latest_tag = _get_latest_git_tag(root_dir)
    if not latest_tag:
        return {
            "release_required": False,
            "mode": "upstream_starter_kit",
            "current_version": APP_VERSION,
            "latest_tag": None,
            "unreleased_commits_count": 0,
            "recommended_bump": None,
            "code_changes_detected": False,
            "content_only_changes": False,
            "reason": "No git tags found or not a valid git repository.",
            "unreleased_commits": [],
        }

    commits = _get_unreleased_commits(root_dir, latest_tag)
    if not commits:
        return {
            "release_required": False,
            "mode": "upstream_starter_kit",
            "current_version": APP_VERSION,
            "latest_tag": latest_tag,
            "unreleased_commits_count": 0,
            "recommended_bump": None,
            "code_changes_detected": False,
            "content_only_changes": False,
            "reason": f"HEAD is aligned with latest tag {latest_tag}. Working tree clean.",
            "unreleased_commits": [],
        }

    return _evaluate_unreleased_diff(root_dir, latest_tag, commits)
