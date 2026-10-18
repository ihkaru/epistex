"""Factory for resolving and instantiating asset storage providers."""

from typing import Optional
from config.cloud import CLOUD_STORAGE_BACKEND, CLOUD_AUTH_MODE
from src.contracts.asset_storage import AssetStorageInterface
from src.contracts.secret_provider import SecretProviderInterface
from .local_provider import LocalAssetProvider
from .s3_provider import S3CompatibleAssetProvider


def create_asset_storage(
    backend: Optional[str] = None,
    auth_mode: Optional[str] = None,
    secret_provider: Optional[SecretProviderInterface] = None,
) -> AssetStorageInterface:
    """Create AssetStorageInterface implementation. Defaults to LocalAssetProvider (opt-in)."""
    selected = (backend or CLOUD_STORAGE_BACKEND).lower()
    selected_auth = (auth_mode or CLOUD_AUTH_MODE).lower()

    if selected == "s3":
        return S3CompatibleAssetProvider(
            auth_mode=selected_auth,
            secret_provider=secret_provider,
        )

    # Default is always local (offline, zero-cost, opt-in)
    return LocalAssetProvider()
