"""Hermetic subprocess execution runner with runtime secret injection."""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from config.vault import SAFE_HOST_ENV_VARS
from src.contracts.code_runner import CodeRunnerInterface, ExecutionResult
from src.contracts.events import EventDispatcherInterface
from src.contracts.secret_provider import SecretProviderInterface
from src.events.domain_events import (
    PreRunExecutionEvent,
    PostRunExecutionEvent,
    SecretInjectedEvent,
)


class HermeticCodeRunner(CodeRunnerInterface):
    """Executes commands in an isolated subprocess with stripped environment and injected secrets."""

    def __init__(
        self,
        secret_provider: SecretProviderInterface,
        event_dispatcher: Optional[EventDispatcherInterface] = None,
        safe_env_vars: Optional[Set[str]] = None,
    ) -> None:
        self.secret_provider = secret_provider
        self.dispatcher = event_dispatcher
        self.safe_env_vars = safe_env_vars or SAFE_HOST_ENV_VARS

    def _prepare_sanitized_environment(
        self, env_overrides: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Strip host environment and inject secrets strictly in memory."""
        sanitized: Dict[str, str] = {
            k: v for k, v in os.environ.items() if k in self.safe_env_vars
        }
        injected = self.secret_provider.inject_env(sanitized)
        if env_overrides:
            injected.update(env_overrides)
        return injected

    def _execute_subprocess(
        self, command: List[str], cwd: Optional[Path], env: Dict[str, str], timeout: Optional[float]
    ) -> Tuple[int, str, str, bool]:
        """Execute child process and capture exit code, stdout, stderr, and timeout flag."""
        try:
            res = subprocess.run(
                command,
                cwd=str(cwd) if cwd else None,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return res.returncode, res.stdout, res.stderr, False
        except subprocess.TimeoutExpired as ex:
            out = ex.stdout or "" if isinstance(ex.stdout, str) else ""
            return 124, out, f"Execution timed out after {timeout}s\n", True
        except Exception as ex:
            return 70, "", f"Failed to execute command: {ex}\n", False

    def run(
        self,
        command: List[str],
        cwd: Optional[Path] = None,
        env_overrides: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        dry_run: bool = False,
    ) -> ExecutionResult:
        """Run command hermetically, capturing streams and timing execution."""
        env = self._prepare_sanitized_environment(env_overrides)
        secret_keys = list(self.secret_provider.get_all_secrets().keys())
        target_str = " ".join(command)

        if self.dispatcher:
            self.dispatcher.dispatch(SecretInjectedEvent(self.secret_provider.get_backend_name(), secret_keys, target_str))
            self.dispatcher.dispatch(PreRunExecutionEvent(command, cwd, len(secret_keys)))

        if dry_run:
            return ExecutionResult(
                exit_code=0,
                stdout=f"[DRY-RUN] Command: {target_str}\nInjected secrets: {len(secret_keys)} keys\n",
                stderr="",
                duration_ms=0.0,
                injected_secret_count=len(secret_keys),
                command=command,
            )

        start = time.perf_counter()
        exit_code, stdout, stderr, timed_out = self._execute_subprocess(command, cwd, env, timeout)
        duration = (time.perf_counter() - start) * 1000.0

        if self.dispatcher:
            self.dispatcher.dispatch(PostRunExecutionEvent(command, exit_code, duration))

        return ExecutionResult(
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration,
            timed_out=timed_out,
            injected_secret_count=len(secret_keys),
            command=command,
        )
