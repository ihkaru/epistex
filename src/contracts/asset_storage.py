"""Contracts for cloud asset offloading and tiered storage."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass(frozen=True)
class AssetDescriptor:
    """Metadata descriptor for a binary asset offloaded to cloud storage."""

    remote_key: str
    sha256: str
    size_bytes: int
    mime_type: str
    backend: str
    url: Optional[str] = None
    local_path: Optional[str] = None
    sync_status: str = "remote"
    extra: Dict[str, str] = field(default_factory=dict)


class AssetStorageInterface(ABC):
    """Abstract contract for cloud and local asset storage providers."""

    @abstractmethod
    def upload(
        self,
        local_path: Path,
        remote_key: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> AssetDescriptor:
        """Upload a local binary asset to storage and return its descriptor."""
        raise NotImplementedError

    @abstractmethod
    def download(self, remote_key: str, target_path: Path) -> Path:
        """Download remote asset by key to local target path."""
        raise NotImplementedError

    @abstractmethod
    def exists(self, remote_key: str) -> bool:
        """Check if remote asset exists in storage."""
        raise NotImplementedError

    @abstractmethod
    def get_url(self, remote_key: str, expires_in: int = 3600) -> str:
        """Generate download or presigned URL for direct asset access."""
        raise NotImplementedError

    @abstractmethod
    def get_backend_name(self) -> str:
        """Human-readable identifier of the storage provider."""
        raise NotImplementedError
