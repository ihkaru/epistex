"""Contracts for document querying, loading, and persistence."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class DocumentMetadata:
    """Parsed document metadata and positional context."""

    path: Path
    title: str
    status: str
    category: str
    owner: str
    end_line: int
    raw_frontmatter: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    deadlines: List[Dict[str, Any]] = field(default_factory=list)


class DocumentRepositoryInterface(ABC):
    """Abstract contract for knowledge base document repository."""

    @abstractmethod
    def find_all(self) -> List[DocumentMetadata]:
        """Find and stream metadata for all valid markdown documents."""
        raise NotImplementedError

    @abstractmethod
    def find_by_path(self, path: Path) -> Optional[DocumentMetadata]:
        """Find document metadata by relative or absolute path."""
        raise NotImplementedError

    @abstractmethod
    def save(self, path: Path, frontmatter: Dict[str, Any], body: str) -> Path:
        """Persist a document atomically with YAML frontmatter and markdown body."""
        raise NotImplementedError
