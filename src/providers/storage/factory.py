"""Factory for resolving and instantiating asset storage providers."""

from typing import Optional
from config.cloud import CLOUD_STORAGE_BACKEND
from src.contracts.asset_storage import AssetStorageInterface
from .local_provider import LocalAssetProvider
from .s3_provider import S3CompatibleAssetProvider


def create_asset_storage(backend: Optional[str] = None) -> AssetStorageInterface:
    """Create AssetStorageInterface implementation. Defaults to LocalAssetProvider (opt-in)."""
    selected = (backend or CLOUD_STORAGE_BACKEND).lower()

    if selected == "s3":
        return S3CompatibleAssetProvider()

    # Default is always local (offline, zero-cost, opt-in)
    return LocalAssetProvider()
