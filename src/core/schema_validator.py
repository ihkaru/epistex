"""Schema validator and self-healing diagnostic issue generator."""

from pathlib import Path
from typing import Any, Dict, List
from config.schema import (
    REQUIRED_FRONTMATTER_FIELDS,
    ALLOWED_STATUSES,
    ALLOWED_CATEGORIES,
)
from src.contracts.schema_validator import SchemaValidatorInterface, ValidationIssue


class SchemaValidator(SchemaValidatorInterface):
    """Enforces frontmatter schema conventions and produces self-correction hints."""

    def __init__(
        self,
        required_fields: List[str] = REQUIRED_FRONTMATTER_FIELDS,
        allowed_statuses: List[str] = ALLOWED_STATUSES,
        allowed_categories: List[str] = ALLOWED_CATEGORIES,
    ) -> None:
        self.required_fields = required_fields
        self.allowed_statuses = allowed_statuses
        self.allowed_categories = allowed_categories

    def _validate_required_fields(
        self, path: Path, frontmatter: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate presence of all mandatory frontmatter fields."""
        issues = []
        for req in self.required_fields:
            if req not in frontmatter or frontmatter[req] in (None, ""):
                issues.append(
                    ValidationIssue(
                        file=path,
                        line=1,
                        field_name=req,
                        message=f"Missing required frontmatter field: '{req}'",
                        error_type="MISSING_REQUIRED_FIELD",
                        fix_hint=f"Define '{req}: <value>' in YAML frontmatter.",
                    )
                )
        return issues

    def _validate_status_and_category(
        self, path: Path, frontmatter: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate status and category values against allowed enumerations."""
        issues = []
        status = str(frontmatter.get("status", "")).lower()
        if status and status not in self.allowed_statuses:
            issues.append(
                ValidationIssue(
                    file=path,
                    line=2,
                    field_name="status",
                    message=f"Invalid document status '{status}'",
                    error_type="INVALID_STATUS",
                    received=status,
                    allowed=self.allowed_statuses,
                    fix_hint=f"Change 'status: {status}' to one of: {', '.join(self.allowed_statuses)}",
                )
            )

        cat = str(frontmatter.get("category", "")).lower()
        if cat and cat not in self.allowed_categories:
            issues.append(
                ValidationIssue(
                    file=path,
                    line=3,
                    field_name="category",
                    message=f"Invalid document category '{cat}'",
                    error_type="INVALID_CATEGORY",
                    received=cat,
                    allowed=self.allowed_categories,
                    fix_hint=f"Change 'category: {cat}' to one of: {', '.join(self.allowed_categories)}",
                )
            )
        return issues

    def validate_document(
        self, path: Path, frontmatter: Dict[str, Any], end_line: int
    ) -> List[ValidationIssue]:
        """Validate frontmatter fields, returning a list of detailed diagnostic issues."""
        if not frontmatter:
            return [
                ValidationIssue(
                    file=path,
                    line=1,
                    field_name="frontmatter",
                    message="Missing or unclosed YAML frontmatter delimiters ('---')",
                    error_type="MISSING_FRONTMATTER",
                    fix_hint="Add valid YAML frontmatter between two '---' markers at top of file.",
                )
            ]

        issues: List[ValidationIssue] = []
        issues.extend(self._validate_required_fields(path, frontmatter))
        issues.extend(self._validate_status_and_category(path, frontmatter))
        return issues
