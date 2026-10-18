"""Secret provider status and connectivity diagnostics command."""

from typing import Any, Dict, List, Optional, Tuple
from config.app import EX_OK
from src.contracts.secret_provider import SecretProviderInterface
from src.providers.secrets.factory import create_secret_provider


def _mask_value(val: str) -> str:
    """Mask secret value for safe diagnostic display."""
    if not val:
        return "<empty>"
    if len(val) <= 4:
        return "***"
    return f"{val[:2]}***{val[-2:]}"


def run_secrets(
    vault_backend: Optional[str] = None,
    secret_provider: Optional[SecretProviderInterface] = None,
) -> Tuple[int, Dict[str, Any]]:
    """Inspect secret provider status, registered keys, and backend health."""
    provider = secret_provider or create_secret_provider(vault_backend)
    is_avail = provider.is_available()
    all_secrets = provider.get_all_secrets() if is_avail else {}

    masked_entries = [
        {"key": k, "masked": _mask_value(v), "length": len(v)}
        for k, v in sorted(all_secrets.items())
    ]

    payload = {
        "status": "ok",
        "exit_code": EX_OK,
        "backend": provider.get_backend_name(),
        "available": is_avail,
        "total_secrets": len(masked_entries),
        "secrets": masked_entries,
    }
    return EX_OK, payload
