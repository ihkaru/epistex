"""Factory for creating and resolving configured secret providers."""

from typing import Optional
from config.vault import VAULT_BACKEND
from src.contracts.secret_provider import SecretProviderInterface
from .env_provider import EnvSecretProvider
from .infisical_provider import InfisicalSecretProvider
from .memory_provider import MemorySecretProvider


def create_secret_provider(backend: Optional[str] = None) -> SecretProviderInterface:
    """Instantiate appropriate SecretProviderInterface implementation based on configuration."""
    selected = (backend or VAULT_BACKEND).lower()

    if selected == "memory":
        return MemorySecretProvider()
    if selected == "env":
        return EnvSecretProvider()
    if selected in ("infisical", "auto"):
        infisical = InfisicalSecretProvider()
        if infisical.is_available():
            return infisical
        return EnvSecretProvider()

    # Fallback to env
    return EnvSecretProvider()
