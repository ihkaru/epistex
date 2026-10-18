"""Frontmatter schema validation definitions and conventions."""

from typing import Dict, Any, List

# Allowed document statuses across knowledge domains
ALLOWED_STATUSES = [
    "draft",
    "active",
    "review",
    "deprecated",
    "superseded",
    "completed",
]

# Allowed document categories / types
ALLOWED_CATEGORIES = [
    "architecture-decision",  # ADR
    "runbook",                # Operational runbook
    "playbook",               # Incident & troubleshooting playbook
    "rfc",                    # Request for comments
    "activity",               # Structured operational activity
    "guideline",              # General engineering or process guideline
]

# Required top-level frontmatter fields
REQUIRED_FRONTMATTER_FIELDS = [
    "title",
    "status",
    "category",
    "owner",
]

# Default frontmatter templates for scaffold generation
DEFAULT_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "adr": {
        "title": "Untitled Architecture Decision Record",
        "status": "draft",
        "category": "architecture-decision",
        "owner": "@team",
        "tags": ["architecture", "decision"],
        "context": "Context and problem statement.",
        "decision": "The proposed technical solution.",
        "consequences": "Trade-offs and blast radius analysis.",
    },
    "runbook": {
        "title": "Untitled Operational Runbook",
        "status": "draft",
        "category": "runbook",
        "owner": "@team",
        "tags": ["ops", "runbook"],
        "preconditions": ["List prerequisite permissions or access."],
        "steps": ["Step 1", "Step 2"],
    },
    "activity": {
        "title": "Untitled Operational Activity",
        "status": "active",
        "category": "activity",
        "owner": "@team",
        "routine": "quarterly",
        "deadlines": [
            {"milestone": "Kickoff", "due": "2026-11-01"},
            {"milestone": "Final Review", "due": "2026-11-15"},
        ],
    },
}
