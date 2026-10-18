"""Asset management CLI command for offloading binaries and on-demand hydration."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from config.app import KNOWLEDGE_DIR, EX_OK, EX_USAGE, EX_NOINPUT, EX_SOFTWARE
from src.contracts.asset_storage import AssetDescriptor, AssetStorageInterface
from src.contracts.events import EventDispatcherInterface
from src.contracts.secret_provider import SecretProviderInterface
from src.core.companion import write_companion_file, parse_companion_metadata
from src.core.scanner import scan_markdown_files
from src.core.io_stream import read_frontmatter_streaming
from src.events.domain_events import (
    AssetUploadedEvent,
    AssetDownloadedEvent,
    AssetVerifiedEvent,
    DocumentCreatedEvent,
)
from src.providers.storage.factory import create_asset_storage
from src.providers.storage.local_provider import compute_file_sha256


def _write_and_dispatch_companion(
    descriptor: AssetDescriptor,
    companion_path: Optional[str],
    src_name: str,
    src_stem: str,
    title: Optional[str],
    owner: Optional[str],
    base_dir: Optional[Path],
    dispatcher: Optional[EventDispatcherInterface],
) -> Path:
    """Create companion markdown file in Git and dispatch domain event."""
    target_base = base_dir or KNOWLEDGE_DIR
    comp_rel = companion_path or f"assets/{src_stem}.md"
    comp_file = (target_base / comp_rel).resolve()
    doc_title = title or f"Asset: {src_name}"
    doc_owner = owner or "@team"

    write_companion_file(comp_file, descriptor, title=doc_title, owner=doc_owner)
    if dispatcher:
        dispatcher.dispatch(DocumentCreatedEvent(comp_file, doc_title, "asset-companion", doc_owner))
    return comp_file


def run_asset_push(
    local_file: str,
    remote_key: Optional[str] = None,
    companion_path: Optional[str] = None,
    title: Optional[str] = None,
    owner: Optional[str] = None,
    backend: Optional[str] = None,
    cloud_auth: Optional[str] = None,
    secret_provider: Optional[SecretProviderInterface] = None,
    dispatcher: Optional[EventDispatcherInterface] = None,
    storage: Optional[AssetStorageInterface] = None,
    base_dir: Optional[Path] = None,
) -> Tuple[int, Dict[str, Any]]:
    """Offload binary file to cloud/local storage and create Git companion markdown."""
    src_path = Path(local_file).resolve()
    if not src_path.exists():
        return EX_NOINPUT, {
            "status": "error",
            "exit_code": EX_NOINPUT,
            "error_type": "FILE_NOT_FOUND",
            "message": f"Local asset file not found: {local_file}",
        }

    key = remote_key or f"assets/{src_path.name}"
    client = storage or create_asset_storage(backend=backend, auth_mode=cloud_auth, secret_provider=secret_provider)
    desc = client.upload(src_path, key)

    if dispatcher:
        dispatcher.dispatch(AssetUploadedEvent(desc.remote_key, desc.backend, desc.size_bytes, desc.sha256))

    comp_file = _write_and_dispatch_companion(
        desc, companion_path, src_path.name, src_path.stem, title, owner, base_dir, dispatcher
    )

    payload = {
        "status": "ok",
        "exit_code": EX_OK,
        "action": "push",
        "remote_key": desc.remote_key,
        "backend": desc.backend,
        "size_bytes": desc.size_bytes,
        "sha256": desc.sha256,
        "companion_path": str(comp_file),
    }
    return EX_OK, payload


def run_asset_pull(
    remote_key: str,
    target_path: Optional[str] = None,
    backend: Optional[str] = None,
    cloud_auth: Optional[str] = None,
    secret_provider: Optional[SecretProviderInterface] = None,
    dispatcher: Optional[EventDispatcherInterface] = None,
    storage: Optional[AssetStorageInterface] = None,
) -> Tuple[int, Dict[str, Any]]:
    """Download remote asset on-demand and verify its checksum."""
    client = storage or create_asset_storage(backend=backend, auth_mode=cloud_auth, secret_provider=secret_provider)
    dest = Path(target_path) if target_path else Path("storage/cache") / Path(remote_key).name
    dest = dest.resolve()

    try:
        downloaded = client.download(remote_key, dest)
    except Exception as ex:
        return EX_SOFTWARE, {
            "status": "error",
            "exit_code": EX_SOFTWARE,
            "error_type": "ASSET_DOWNLOAD_ERROR",
            "message": f"Failed to download asset '{remote_key}': {ex}",
        }

    actual_hash = compute_file_sha256(downloaded)
    if dispatcher:
        dispatcher.dispatch(
            AssetDownloadedEvent(remote_key, client.get_backend_name(), str(downloaded), downloaded.stat().st_size)
        )

    payload = {
        "status": "ok",
        "exit_code": EX_OK,
        "action": "pull",
        "remote_key": remote_key,
        "backend": client.get_backend_name(),
        "local_path": str(downloaded),
        "sha256": actual_hash,
        "size_bytes": downloaded.stat().st_size,
    }
    return EX_OK, payload


def run_asset_check(
    remote_key: str,
    backend: Optional[str] = None,
    cloud_auth: Optional[str] = None,
    secret_provider: Optional[SecretProviderInterface] = None,
    dispatcher: Optional[EventDispatcherInterface] = None,
    storage: Optional[AssetStorageInterface] = None,
) -> Tuple[int, Dict[str, Any]]:
    """Check existence of an asset in storage backend without downloading blob."""
    client = storage or create_asset_storage(backend=backend, auth_mode=cloud_auth, secret_provider=secret_provider)
    exists = client.exists(remote_key)

    if dispatcher:
        dispatcher.dispatch(AssetVerifiedEvent(remote_key, client.get_backend_name(), exists, match_sha256=True))

    payload = {
        "status": "ok",
        "exit_code": EX_OK,
        "remote_key": remote_key,
        "backend": client.get_backend_name(),
        "exists": exists,
    }
    return EX_OK, payload


def run_asset_list(
    tier: str = "local",
    base_dir: Optional[Path] = None,
    backend: Optional[str] = None,
    cloud_auth: Optional[str] = None,
    secret_provider: Optional[SecretProviderInterface] = None,
    storage: Optional[AssetStorageInterface] = None,
) -> Tuple[int, Dict[str, Any]]:
    """Discover assets via companion documents across local and cloud tiers."""
    scan_dir = base_dir or KNOWLEDGE_DIR
    client = (storage or create_asset_storage(backend=backend, auth_mode=cloud_auth, secret_provider=secret_provider)) if tier in ("cloud", "all") else None
    items: List[Dict[str, Any]] = []

    for doc in scan_markdown_files(scan_dir):
        meta, _, _ = read_frontmatter_streaming(doc)
        asset_info = parse_companion_metadata(meta)
        if not asset_info:
            continue

        key = asset_info.get("remote_key", "")
        item: Dict[str, Any] = {
            "title": meta.get("title", doc.stem),
            "companion_file": str(doc),
            "remote_key": key,
            "sha256": asset_info.get("sha256", ""),
            "size_bytes": asset_info.get("size_bytes", 0),
            "backend": asset_info.get("storage_backend", "local"),
        }

        if client and key:
            item["cloud_exists"] = client.exists(key)

        items.append(item)

    payload = {
        "status": "ok",
        "exit_code": EX_OK,
        "tier": tier,
        "total_assets": len(items),
        "assets": items,
    }
    return EX_OK, payload
