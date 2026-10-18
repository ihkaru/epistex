"""Contracts for schema validation and diagnostic envelope generation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ValidationIssue:
    """Detailed validation diagnostic issue."""

    file: Path
    line: int
    field_name: str
    message: str
    error_type: str
    received: Any = None
    allowed: List[Any] = field(default_factory=list)
    fix_hint: str = ""


class SchemaValidatorInterface(ABC):
    """Abstract contract for knowledge base schema validation."""

    @abstractmethod
    def validate_document(
        self, path: Path, frontmatter: Dict[str, Any], end_line: int
    ) -> List[ValidationIssue]:
        """Validate parsed document frontmatter and return diagnostic issues."""
        raise NotImplementedError
