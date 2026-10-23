"""In-memory secret provider for isolated tests and hermetic pipelines."""

from typing import Dict, Optional
from src.contracts.secret_provider import SecretProviderInterface


class MemorySecretProvider(SecretProviderInterface):
    """In-memory key-value secret provider."""

    def __init__(self, initial_secrets: Optional[Dict[str, str]] = None) -> None:
        self._secrets: Dict[str, str] = dict(initial_secrets or {})

    def set_secret(self, key: str, value: str) -> None:
        """Store or update a secret in memory."""
        self._secrets[key] = value

    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a secret by key."""
        return self._secrets.get(key)

    def get_all_secrets(self) -> Dict[str, str]:
        """Retrieve all in-memory secrets."""
        return dict(self._secrets)

    def inject_env(self, base_env: Dict[str, str]) -> Dict[str, str]:
        """Inject in-memory secrets into target environment dictionary."""
        new_env = dict(base_env)
        new_env.update(self._secrets)
        return new_env

    def is_available(self) -> bool:
        """Check availability of in-memory secret store."""
        return isinstance(self._secrets, dict)

    def get_backend_name(self) -> str:
        return "memory"
