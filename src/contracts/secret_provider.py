"""Contracts for secret management and runtime secret injection."""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class SecretProviderInterface(ABC):
    """Abstract contract for secret providers."""

    @abstractmethod
    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a single secret by key."""
        raise NotImplementedError

    @abstractmethod
    def get_all_secrets(self) -> Dict[str, str]:
        """Retrieve all accessible secrets as key-value pairs."""
        raise NotImplementedError

    @abstractmethod
    def inject_env(self, base_env: Dict[str, str]) -> Dict[str, str]:
        """Inject secrets into an environment mapping in memory."""
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this secret provider backend is reachable and available."""
        raise NotImplementedError

    @abstractmethod
    def get_backend_name(self) -> str:
        """Human-readable identifier for this secret backend."""
        raise NotImplementedError
