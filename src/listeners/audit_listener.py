"""Audit event listener recording immutable execution history to JSONL."""

import json
from pathlib import Path
from typing import Optional
from config.app import LOGS_DIR
from src.contracts.events import EventInterface


class AuditEventListener:
    """Appends domain events to structured audit JSONL log in storage."""

    def __init__(self, log_path: Optional[Path] = None) -> None:
        self.log_path = log_path or (LOGS_DIR / "audit.jsonl")

    def handle(self, event: EventInterface) -> None:
        """Handle incoming domain event and record to audit log."""
        record = {
            "timestamp": event.timestamp,
            "event": event.name,
            "payload": event.payload,
        }
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except OSError:
            pass
