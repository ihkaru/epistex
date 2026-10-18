"""Local filesystem asset storage provider (offline default, zero-dependency)."""

import hashlib
import mimetypes
import os
import shutil
from pathlib import Path
from typing import Dict, Optional
from config.cloud import LOCAL_ASSET_DIR, DEFAULT_CHUNK_SIZE
from src.contracts.asset_storage import AssetDescriptor, AssetStorageInterface


def compute_file_sha256(path: Path, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    """Compute SHA-256 hash using chunk streaming in O(1) memory."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


class LocalAssetProvider(AssetStorageInterface):
    """Local storage provider saving binary assets to local cache directory."""

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self.base_dir = (base_dir or LOCAL_ASSET_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_target(self, remote_key: str) -> Path:
        """Resolve cleaned destination path under base directory."""
        clean_key = remote_key.lstrip("/").replace("\\", "/")
        return (self.base_dir / clean_key).resolve()

    def upload(
        self,
        local_path: Path,
        remote_key: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> AssetDescriptor:
        """Copy local asset to local asset cache and return its descriptor."""
        if not local_path.exists():
            raise FileNotFoundError(f"Local asset not found: {local_path}")

        target = self._resolve_target(remote_key)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local_path, target)

        size = target.stat().st_size
        sha256_hash = compute_file_sha256(target)
        mime, _ = mimetypes.guess_type(str(local_path))

        return AssetDescriptor(
            remote_key=remote_key,
            sha256=sha256_hash,
            size_bytes=size,
            mime_type=mime or "application/octet-stream",
            backend="local",
            url=f"file://{target.as_posix()}",
            local_path=str(target),
            sync_status="synced",
        )

    def download(self, remote_key: str, target_path: Path) -> Path:
        """Copy cached asset to destination path."""
        source = self._resolve_target(remote_key)
        if not source.exists():
            raise FileNotFoundError(f"Asset key '{remote_key}' not found in local storage.")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target_path)
        return target_path

    def exists(self, remote_key: str) -> bool:
        """Check if asset exists in local asset storage."""
        return self._resolve_target(remote_key).exists()

    def get_url(self, remote_key: str, expires_in: int = 3600) -> str:
        """Return file URI for local asset."""
        target = self._resolve_target(remote_key)
        return f"file://{target.as_posix()}"

    def get_backend_name(self) -> str:
        return "local"
