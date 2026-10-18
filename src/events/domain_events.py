"""Concrete domain events for lifecycle hooks and audit logging."""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.contracts.events import EventInterface


class BaseDomainEvent(EventInterface):
    """Base class for all domain events."""

    def __init__(self, name: str, payload: Optional[Dict[str, Any]] = None) -> None:
        self._name = name
        self._timestamp = time.time()
        self._payload = payload or {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def payload(self) -> Dict[str, Any]:
        return self._payload


class DocumentCreatedEvent(BaseDomainEvent):
    """Triggered when a document is created or updated in the knowledge base."""

    def __init__(self, path: Path, title: str, category: str, owner: str) -> None:
        super().__init__(
            "document.created",
            {
                "path": str(path),
                "title": title,
                "category": category,
                "owner": owner,
            },
        )


class FrontmatterParsedEvent(BaseDomainEvent):
    """Triggered when frontmatter is extracted from a document stream."""

    def __init__(self, path: Path, frontmatter: Dict[str, Any], end_line: int) -> None:
        super().__init__(
            "document.frontmatter_parsed",
            {
                "path": str(path),
                "frontmatter": frontmatter,
                "end_line": end_line,
            },
        )


class SecretInjectedEvent(BaseDomainEvent):
    """Triggered when secrets are injected into an execution runtime."""

    def __init__(self, backend: str, secret_keys: List[str], target_command: str) -> None:
        super().__init__(
            "vault.secret_injected",
            {
                "backend": backend,
                "secret_count": len(secret_keys),
                "secret_keys": secret_keys,
                "target_command": target_command,
            },
        )


class PreRunExecutionEvent(BaseDomainEvent):
    """Triggered before executing a hermetic command."""

    def __init__(self, command: List[str], cwd: Optional[Path], secret_count: int) -> None:
        super().__init__(
            "runner.pre_run",
            {
                "command": command,
                "cwd": str(cwd) if cwd else None,
                "secret_count": secret_count,
            },
        )


class PostRunExecutionEvent(BaseDomainEvent):
    """Triggered after completing hermetic execution."""

    def __init__(self, command: List[str], exit_code: int, duration_ms: float) -> None:
        super().__init__(
            "runner.post_run",
            {
                "command": command,
                "exit_code": exit_code,
                "duration_ms": duration_ms,
            },
        )


class HealthCheckCompletedEvent(BaseDomainEvent):
    """Triggered when repository health audit completes."""

    def __init__(self, total_files: int, issue_count: int, dead_link_count: int) -> None:
        super().__init__(
            "doctor.completed",
            {
                "total_files": total_files,
                "issue_count": issue_count,
                "dead_link_count": dead_link_count,
            },
        )
