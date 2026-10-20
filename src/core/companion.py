"""Helper utilities for Git-native companion markdown documents."""

from pathlib import Path
from typing import Any, Dict, Optional
from config.app import KNOWLEDGE_DIR
from src.contracts.asset_storage import AssetDescriptor
from src.core.io_stream import atomic_write_text


def format_companion_markdown(
    asset: AssetDescriptor,
    title: str,
    owner: str = "@team",
    description: str = "",
) -> str:
    """Format standard companion markdown containing YAML frontmatter and pull instructions."""
    desc = description or f"Git companion pointer to binary asset offloaded to {asset.backend} storage."
    gx_cmd = f"gx asset pull {asset.remote_key}"

    lines = [
        "---",
        f"title: \"{title}\"",
        "status: active",
        "category: asset-companion",
        f"owner: \"{owner}\"",
        "asset:",
        f"  remote_key: \"{asset.remote_key}\"",
        f"  sha256: \"{asset.sha256}\"",
        f"  size_bytes: {asset.size_bytes}",
        f"  mime_type: \"{asset.mime_type}\"",
        f"  storage_backend: \"{asset.backend}\"",
        f"  sync_status: \"{asset.sync_status}\"",
        "---",
        "",
        f"# {title}",
        "",
        desc,
        "",
        "## Asset Specifications",
        f"- **Remote Key**: `{asset.remote_key}`",
        f"- **Storage Backend**: `{asset.backend}`",
        f"- **File Size**: `{asset.size_bytes}` bytes",
        f"- **SHA-256 Checksum**: `{asset.sha256}`",
        f"- **MIME Type**: `{asset.mime_type}`",
        "",
        "## On-Demand Hydration",
        "To download or cache this binary asset locally on demand:",
        "```bash",
        gx_cmd,
        "```",
        "",
    ]
    return "\n".join(lines)


def write_companion_file(
    companion_path: Path,
    asset: AssetDescriptor,
    title: str,
    owner: str = "@team",
    description: str = "",
) -> Path:
    """Atomically write companion markdown document to disk."""
    content = format_companion_markdown(asset, title, owner, description)
    atomic_write_text(companion_path, content)
    return companion_path


def parse_companion_metadata(frontmatter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract and validate asset block from companion markdown frontmatter."""
    if frontmatter.get("category") != "asset-companion":
        return None
    asset_block = frontmatter.get("asset")
    if isinstance(asset_block, dict) and "remote_key" in asset_block:
        return asset_block
    if "remote_key" in frontmatter:
        return frontmatter
    return None

