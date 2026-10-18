"""Environment-variable and .env based secret provider (zero vendor lock-in)."""

import os
from pathlib import Path
from typing import Dict, Optional
from src.contracts.secret_provider import SecretProviderInterface


class EnvSecretProvider(SecretProviderInterface):
    """Provides secrets directly from process environment and optional local .env."""

    def __init__(self, env_file: Optional[Path] = None) -> None:
        self.env_file = env_file or Path(".env")
        self._cache: Dict[str, str] = {}
        self._load_local_env()

    def _load_local_env(self) -> None:
        """Parse local .env file in memory if it exists, without writing to disk."""
        if not self.env_file.exists():
            return
        try:
            with open(self.env_file, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#") or "=" not in stripped:
                        continue
                    k, v = stripped.split("=", 1)
                    key = k.strip()
                    val = v.strip().strip("'\"")
                    self._cache[key] = val
        except OSError:
            pass

    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a secret from process environment or loaded .env file."""
        if key in os.environ:
            return os.environ[key]
        return self._cache.get(key)

    def get_all_secrets(self) -> Dict[str, str]:
        """Combine process environment with local .env."""
        combined = dict(self._cache)
        combined.update(os.environ)
        return combined

    def inject_env(self, base_env: Dict[str, str]) -> Dict[str, str]:
        """Inject all secrets into a target environment dictionary in memory."""
        new_env = dict(base_env)
        new_env.update(self.get_all_secrets())
        return new_env

    def is_available(self) -> bool:
        """Environment provider is always universally available."""
        return True

    def get_backend_name(self) -> str:
        return "env"
