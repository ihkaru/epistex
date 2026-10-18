"""Telemetry listener reporting diagnostics strictly to STDERR."""

import sys
from src.contracts.events import EventInterface


class TelemetryEventListener:
    """Prints diagnostic milestones and timing to STDERR preserving STDOUT stream purity."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def handle(self, event: EventInterface) -> None:
        """Output diagnostic trace to STDERR if telemetry is enabled."""
        if not self.enabled:
            return
        if event.name == "runner.post_run":
            cmd = " ".join(event.payload.get("command", []))
            code = event.payload.get("exit_code")
            duration = event.payload.get("duration_ms", 0.0)
            sys.stderr.write(f"[Telemetry] Command finished in {duration:.2f}ms (exit code: {code}): {cmd}\n")
        elif event.name == "doctor.completed":
            total = event.payload.get("total_files", 0)
            issues = event.payload.get("issue_count", 0)
            sys.stderr.write(f"[Telemetry] Audit complete: {total} files scanned, {issues} issues found.\n")
