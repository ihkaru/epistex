"""Hermetic code runner command with runtime Infisical secret injection."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from config.app import EX_OK, EX_USAGE, EX_SOFTWARE
from src.contracts.events import EventDispatcherInterface
from src.contracts.secret_provider import SecretProviderInterface
from src.providers.runner.hermetic_runner import HermeticCodeRunner
from src.providers.secrets.factory import create_secret_provider


def run_code(
    command: List[str],
    cwd: Optional[Path] = None,
    vault_backend: Optional[str] = None,
    timeout: Optional[float] = None,
    dry_run: bool = False,
    dispatcher: Optional[EventDispatcherInterface] = None,
    secret_provider: Optional[SecretProviderInterface] = None,
) -> Tuple[int, Dict[str, Any]]:
    """Execute command in isolated hermetic environment with injected secrets."""
    if not command:
        return EX_USAGE, {
            "status": "error",
            "exit_code": EX_USAGE,
            "error_type": "EMPTY_COMMAND",
            "message": "No command specified. Usage: gx run [--dry-run] -- <command>",
        }

    provider = secret_provider or create_secret_provider(vault_backend)
    runner = HermeticCodeRunner(
        secret_provider=provider,
        event_dispatcher=dispatcher,
    )

    result = runner.run(
        command=command,
        cwd=cwd,
        timeout=timeout,
        dry_run=dry_run,
    )

    status_str = "ok" if result.exit_code == 0 else "error"
    payload = {
        "status": status_str,
        "exit_code": result.exit_code,
        "command": command,
        "duration_ms": result.duration_ms,
        "timed_out": result.timed_out,
        "injected_secrets": result.injected_secret_count,
        "vault_backend": provider.get_backend_name(),
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    return result.exit_code, payload
