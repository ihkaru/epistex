"""Domain exceptions and deterministic POSIX/BSD sysexits error envelopes."""

from typing import Any, Dict, List, Optional
from config.app import EX_USAGE, EX_DATAERR, EX_NOINPUT, EX_SOFTWARE, EX_CONFIG


class KBError(Exception):
    """Base exception for all knowledge base errors."""

    def __init__(self, message: str, exit_code: int = EX_SOFTWARE) -> None:
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code

    def to_envelope(self) -> Dict[str, Any]:
        """Convert exception to agent-first structured error envelope."""
        return {
            "status": "error",
            "exit_code": self.exit_code,
            "error_type": self.__class__.__name__,
            "message": self.message,
        }


class UsageError(KBError):
    """Command-line syntax or invocation error."""

    def __init__(self, message: str, usage: str = "") -> None:
        super().__init__(message, exit_code=EX_USAGE)
        self.usage = usage

    def to_envelope(self) -> Dict[str, Any]:
        envelope = super().to_envelope()
        if self.usage:
            envelope["usage"] = self.usage
        return envelope


class ValidationError(KBError):
    """Frontmatter or document schema validation error."""

    def __init__(
        self,
        message: str,
        file: Optional[str] = None,
        line: int = 1,
        field: str = "",
        received: Any = None,
        allowed: Optional[List[Any]] = None,
        fix_hint: str = "",
    ) -> None:
        super().__init__(message, exit_code=EX_DATAERR)
        self.file = file
        self.line = line
        self.field = field
        self.received = received
        self.allowed = allowed or []
        self.fix_hint = fix_hint

    def to_envelope(self) -> Dict[str, Any]:
        return {
            "status": "error",
            "exit_code": self.exit_code,
            "error_type": "SCHEMA_VALIDATION_ERROR",
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "field": self.field,
            "received": self.received,
            "allowed": self.allowed,
            "fix_hint": self.fix_hint,
        }


class FileNotFoundKBError(KBError):
    """Requested knowledge base document or resource not found."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Document not found: {path}", exit_code=EX_NOINPUT)
        self.path = path

    def to_envelope(self) -> Dict[str, Any]:
        envelope = super().to_envelope()
        envelope["file"] = self.path
        envelope["fix_hint"] = "Verify the document path or run 'ep create' to scaffold it."
        return envelope


class RunnerError(KBError):
    """Execution runner failure or timeout."""

    def __init__(self, message: str, command: Optional[List[str]] = None, exit_code: int = EX_SOFTWARE) -> None:
        super().__init__(message, exit_code=exit_code)
        self.command = command or []

    def to_envelope(self) -> Dict[str, Any]:
        envelope = super().to_envelope()
        envelope["command"] = self.command
        return envelope


class VaultError(KBError):
    """Secret provider or vault connectivity error."""

    def __init__(self, message: str, backend: str = "unknown") -> None:
        super().__init__(message, exit_code=EX_CONFIG)
        self.backend = backend

    def to_envelope(self) -> Dict[str, Any]:
        envelope = super().to_envelope()
        envelope["backend"] = self.backend
        envelope["fix_hint"] = "Check Infisical credentials or set EPISTEX_VAULT_BACKEND=env for fallback."
        return envelope
