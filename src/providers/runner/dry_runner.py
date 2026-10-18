"""Dry-run simulation runner for zero-side-effect verification."""

from pathlib import Path
from typing import Dict, List, Optional
from src.contracts.code_runner import CodeRunnerInterface, ExecutionResult


class DryCodeRunner(CodeRunnerInterface):
    """Simulates command execution safely without spawning processes."""

    def run(
        self,
        command: List[str],
        cwd: Optional[Path] = None,
        env_overrides: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        dry_run: bool = True,
    ) -> ExecutionResult:
        cmd_str = " ".join(command)
        cwd_str = str(cwd) if cwd else "."
        return ExecutionResult(
            exit_code=0,
            stdout=f"[DRY-RUN] Command '{cmd_str}' in '{cwd_str}' simulated successfully.\n",
            stderr="",
            duration_ms=0.0,
            injected_secret_count=len(env_overrides or {}),
            command=command,
        )
