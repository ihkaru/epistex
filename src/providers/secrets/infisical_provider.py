"""First-party Infisical secret provider with memory-only extraction."""

import json
import os
import shutil
import subprocess
import sys
from typing import Any, Dict, Optional
from config.vault import (
    INFISICAL_API_URL,
    INFISICAL_PROJECT_ID,
    INFISICAL_ENVIRONMENT,
    INFISICAL_SECRET_PATH,
)
from src.contracts.secret_provider import SecretProviderInterface
from .env_provider import EnvSecretProvider


def parse_infisical_payload(data: Any) -> Dict[str, str]:
    """Parse JSON payload from infisical export or secrets commands."""
    if isinstance(data, dict):
        return {str(k): str(v) for k, v in data.items()}
    if isinstance(data, list):
        parsed: Dict[str, str] = {}
        for item in data:
            if not isinstance(item, dict):
                continue
            k = item.get("key") or item.get("secretKey")
            v = item.get("value") if "value" in item else item.get("secretValue", "")
            if k:
                parsed[str(k)] = str(v)
        return parsed
    return {}


class InfisicalSecretProvider(SecretProviderInterface):
    """Retrieves secrets dynamically from Infisical CLI over TLS with zero disk writes."""

    def __init__(
        self,
        project_id: str = INFISICAL_PROJECT_ID,
        environment: str = INFISICAL_ENVIRONMENT,
        domain: str = INFISICAL_API_URL,
        secret_path: str = INFISICAL_SECRET_PATH,
        fallback_provider: Optional[SecretProviderInterface] = None,
    ) -> None:
        self.project_id = project_id
        self.environment = environment
        self.domain = domain
        self.secret_path = secret_path
        self.fallback = fallback_provider or EnvSecretProvider()
        self._cached_secrets: Optional[Dict[str, str]] = None

    def is_available(self) -> bool:
        """Check if infisical binary exists on system PATH."""
        return shutil.which("infisical") is not None

    def _fetch_secrets_from_cli(self) -> Dict[str, str]:
        """Fetch secrets in memory via infisical export --format=json."""
        if not self.is_available():
            return self.fallback.get_all_secrets()

        cmd = [
            "infisical",
            "export",
            "--format=json",
            f"--domain={self.domain}",
            f"--projectId={self.project_id}",
            f"--env={self.environment}",
            f"--path={self.secret_path}",
        ]
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=10.0,
            )
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout)
                return parse_infisical_payload(data)
            sys.stderr.write(
                f"[Infisical] Warning: CLI returned code {res.returncode}. Falling back to env.\n"
            )
        except Exception as ex:
            sys.stderr.write(f"[Infisical] Warning: Failed to fetch secrets ({ex}). Falling back to env.\n")

        return self.fallback.get_all_secrets()

    def get_all_secrets(self) -> Dict[str, str]:
        """Retrieve all secrets, caching in memory for the lifecycle of current CLI process."""
        if self._cached_secrets is None:
            self._cached_secrets = self._fetch_secrets_from_cli()
        return self._cached_secrets

    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a specific secret key."""
        secrets = self.get_all_secrets()
        return secrets.get(key)

    def inject_env(self, base_env: Dict[str, str]) -> Dict[str, str]:
        """Inject fetched secrets into target process environment in memory."""
        new_env = dict(base_env)
        new_env.update(self.get_all_secrets())
        return new_env

    def get_backend_name(self) -> str:
        return "infisical"
