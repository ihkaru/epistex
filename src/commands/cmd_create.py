"""Idempotent scaffold generator creating standard markdown documents atomically."""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from config.app import KNOWLEDGE_DIR, EX_OK, EX_USAGE
from config.schema import DEFAULT_TEMPLATES
from src.contracts.events import EventDispatcherInterface
from src.core.io_stream import atomic_write_text
from src.events.domain_events import DocumentCreatedEvent


def _format_frontmatter_yaml(meta: Dict[str, Any]) -> str:
    """Format dictionary into valid standard YAML frontmatter block."""
    lines = ["---"]
    for k, v in meta.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                if isinstance(item, dict):
                    first = True
                    for sub_k, sub_v in item.items():
                        prefix = "  - " if first else "    "
                        lines.append(f"{prefix}{sub_k}: {sub_v}")
                        first = False
                else:
                    lines.append(f"  - {item}")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---\n")
    return "\n".join(lines)


def _prepare_document_content(
    template_key: str, title: Optional[str], owner: Optional[str]
) -> Tuple[Dict[str, Any], str]:
    """Prepare frontmatter metadata and initial body content from template."""
    data = dict(DEFAULT_TEMPLATES[template_key])
    if title:
        data["title"] = title
    if owner:
        data["owner"] = owner
    frontmatter_block = _format_frontmatter_yaml(data)
    body = f"# {data['title']}\n\nDocument details and operational notes.\n"
    return data, frontmatter_block + body


def run_create(
    template_type: str,
    target_rel_path: str,
    title: Optional[str] = None,
    owner: Optional[str] = None,
    force: bool = False,
    dispatcher: Optional[EventDispatcherInterface] = None,
) -> Tuple[int, Dict[str, Any]]:
    """Create a new standardized knowledge base document atomically."""
    template_key = template_type.lower()
    if template_key not in DEFAULT_TEMPLATES:
        allowed = list(DEFAULT_TEMPLATES.keys())
        return EX_USAGE, {
            "status": "error",
            "exit_code": EX_USAGE,
            "error_type": "INVALID_TEMPLATE",
            "message": f"Unknown template '{template_type}'. Allowed: {', '.join(allowed)}",
        }

    target_path = (KNOWLEDGE_DIR / target_rel_path).resolve()
    if target_path.exists() and not force:
        return EX_USAGE, {
            "status": "error",
            "exit_code": EX_USAGE,
            "error_type": "FILE_ALREADY_EXISTS",
            "message": f"Document already exists at '{target_path}'. Pass --force to overwrite.",
            "file": str(target_path),
        }

    data, content = _prepare_document_content(template_key, title, owner)
    atomic_write_text(target_path, content)

    if dispatcher:
        dispatcher.dispatch(
            DocumentCreatedEvent(target_path, data["title"], data["category"], data["owner"])
        )

    return EX_OK, {
        "status": "ok",
        "exit_code": EX_OK,
        "message": f"Successfully created {template_type} document.",
        "path": str(target_path),
        "category": data["category"],
        "title": data["title"],
    }
