"""Repository initialization and onboarding command (Installer)."""

import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config.app import (
    APP_NAME,
    APP_DESCRIPTION,
    EX_OK,
    ROOT_DIR,
)
from src.contracts.events import EventDispatcherInterface
from src.core.io_stream import atomic_write_text
from src.events.domain_events import RepositoryInitializedEvent


def _update_app_config(root_dir: Path, name: str, description: str, dry_run: bool) -> bool:
    """Update APP_NAME, APP_DESCRIPTION, and deactivate starter kit mode inside config/app.py."""
    config_file = root_dir / "config" / "app.py"
    if not config_file.exists():
        return False

    content = config_file.read_text(encoding="utf-8")
    content = re.sub(r'APP_NAME = ".*?"', f'APP_NAME = "{name}"', content)
    content = re.sub(r'APP_DESCRIPTION = ".*?"', f'APP_DESCRIPTION = "{description}"', content)
    content = re.sub(r'IS_STARTER_KIT = True', 'IS_STARTER_KIT = False', content)

    if not dry_run:
        atomic_write_text(config_file, content)
    return True


def _ensure_env_file(root_dir: Path, dry_run: bool) -> bool:
    """Ensure .env exists by copying .env.example if missing."""
    env_file = root_dir / ".env"
    example_file = root_dir / ".env.example"
    if env_file.exists() or not example_file.exists():
        return False

    if not dry_run:
        atomic_write_text(env_file, example_file.read_text(encoding="utf-8"))
    return True


def _prune_maintainer_docs(root_dir: Path, dry_run: bool) -> List[str]:
    """Remove upstream starter kit maintainer release protocols to prevent prompt poisoning."""
    maintainer_docs = [
        root_dir / "docs" / "RELEASING.md",
    ]
    pruned = []
    for file_path in maintainer_docs:
        if file_path.exists():
            pruned.append(str(file_path.relative_to(root_dir)))
            if not dry_run:
                file_path.unlink()
    return pruned


def _activate_githooks(root_dir: Path, dry_run: bool) -> bool:
    """Wire .githooks/ as the active git hooks directory for downstream enforcement."""
    githooks_dir = root_dir / ".githooks"
    pre_commit = githooks_dir / "pre-commit"
    if not githooks_dir.exists() or not pre_commit.exists():
        return False
    if not dry_run:
        pre_commit.chmod(pre_commit.stat().st_mode | 0o111)
        os.system(f"git -C {root_dir} config core.hooksPath .githooks 2>/dev/null")
    return True


def _prune_sample_documents(root_dir: Path, dry_run: bool) -> List[str]:
    """Remove boilerplate sample documents upon specialization."""
    samples = [
        root_dir / "knowledge" / "engineering" / "adr" / "ADR-001-event-driven-architecture.md",
        root_dir / "knowledge" / "engineering" / "adr" / "ADR-001-hybrid-cloud-storage.md",
        root_dir / "knowledge" / "activities" / "quarterly-audit" / "2026-Q4" / "README.md",
    ]
    pruned = []
    for file_path in samples:
        if file_path.exists():
            pruned.append(str(file_path.relative_to(root_dir)))
            if not dry_run:
                file_path.unlink()
    return pruned


def _clean_readme_specialization(root_dir: Path, name: str, description: str, dry_run: bool) -> bool:
    """Clean the specialization checklist notice from README.md."""
    readme_path = root_dir / "README.md"
    if not readme_path.exists():
        return False

    content = readme_path.read_text(encoding="utf-8")
    pattern = r"> \[!IMPORTANT\]\s+> \*\*Starter Kit Specialization Notice.*?\n---\n\n## Key Highlights"
    replacement = (
        f"> [!NOTE]\n"
        f"> **Active Knowledge Base**: Initialized for **{name}** — *{description}*.\n\n"
        f"---\n\n## Key Highlights"
    )
    new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    if count > 0:
        if not dry_run:
            atomic_write_text(readme_path, new_content)
        return True
    return False


def _resolve_init_inputs(
    name: Optional[str],
    description: Optional[str],
    owner: Optional[str],
    interactive: bool,
) -> Tuple[str, str, str]:
    """Resolve input values from CLI flags or interactive prompts."""
    resolved_name = name
    resolved_desc = description
    resolved_owner = owner

    if interactive and sys.stdin.isatty():
        resolved_name = resolved_name or input(f"Project Name [{APP_NAME}]: ").strip()
        resolved_desc = resolved_desc or input(f"Description [{APP_DESCRIPTION}]: ").strip()
        resolved_owner = resolved_owner or input("Default Owner Handle [@team]: ").strip()

    final_name = resolved_name or APP_NAME
    final_desc = resolved_desc or APP_DESCRIPTION
    final_owner = resolved_owner or "@team"
    return final_name, final_desc, final_owner


def run_init(
    name: Optional[str] = None,
    description: Optional[str] = None,
    owner: Optional[str] = None,
    clean_samples: bool = False,
    clean_notice: bool = True,
    dry_run: bool = False,
    interactive: bool = True,
    root_dir: Optional[Path] = None,
    dispatcher: Optional[EventDispatcherInterface] = None,
) -> Tuple[int, Dict[str, Any]]:
    """Initialize and specialize Epistex repository for an organization."""
    base_dir = root_dir or ROOT_DIR
    final_name, final_desc, final_owner = _resolve_init_inputs(name, description, owner, interactive)

    _update_app_config(base_dir, final_name, final_desc, dry_run)
    env_created = _ensure_env_file(base_dir, dry_run)
    pruned_files = _prune_sample_documents(base_dir, dry_run) if clean_samples else []
    pruned_maintainer = _prune_maintainer_docs(base_dir, dry_run)
    notice_cleaned = _clean_readme_specialization(base_dir, final_name, final_desc, dry_run) if clean_notice else False
    hooks_activated = _activate_githooks(base_dir, dry_run)

    if dispatcher and not dry_run:
        dispatcher.dispatch(
            RepositoryInitializedEvent(
                name=final_name,
                description=final_desc,
                owner=final_owner,
                cleaned_samples=clean_samples,
            )
        )

    return EX_OK, {
        "status": "ok",
        "action": "repository_initialized",
        "name": final_name,
        "description": final_desc,
        "owner": final_owner,
        "starter_kit_mode": False,
        "dry_run": dry_run,
        "env_file_created": env_created,
        "samples_pruned": pruned_files,
        "maintainer_docs_pruned": pruned_maintainer,
        "specialization_notice_cleaned": notice_cleaned,
        "githooks_activated": hooks_activated,
    }
