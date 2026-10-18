"""Contracts for hermetic code execution and command runners."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class ExecutionResult:
    """Immutable result from a command or script execution."""

    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    timed_out: bool = False
    injected_secret_count: int = 0
    command: List[str] = field(default_factory=list)


class CodeRunnerInterface(ABC):
    """Abstract contract for executing commands in isolated environments."""

    @abstractmethod
    def run(
        self,
        command: List[str],
        cwd: Optional[Path] = None,
        env_overrides: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        dry_run: bool = False,
    ) -> ExecutionResult:
        """Execute a command hermetically with injected environment."""
        raise NotImplementedError
