"""Base command abstraction and agent-first deterministic argument parser."""

import argparse
import json
import sys
from typing import Any, Dict, List
from config.app import EX_USAGE


class AgentArgumentParser(argparse.ArgumentParser):
    """Subclass of ArgumentParser ensuring machine-pure JSON error envelopes for agents."""

    def error(self, message: str) -> None:
        """Handle CLI usage errors deterministically without freeform text pollution."""
        if "--json" in sys.argv or not sys.stdout.isatty():
            payload = {
                "status": "error",
                "exit_code": EX_USAGE,
                "error_type": "CLI_USAGE_ERROR",
                "message": message,
                "usage": self.format_usage().strip(),
            }
            sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            sys.exit(EX_USAGE)
        super().error(message)


def add_common_flags(parser: argparse.ArgumentParser) -> None:
    """Register common flags across all CLI subcommands."""
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-parseable pure JSON strictly to STDOUT",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Produce token-budget preserving compact output",
    )
    parser.add_argument(
        "-y",
        "--yes",
        "--non-interactive",
        dest="non_interactive",
        action="store_true",
        help="Bypass interactive prompts for autonomous agent execution",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without modifying disk or spawning processes",
    )


def output_result(payload: Dict[str, Any], is_json: bool, tty_formatter: Any = None) -> None:
    """Output result enforcing stream purity between STDOUT data and STDERR logs."""
    if is_json or not sys.stdout.isatty():
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        if tty_formatter and callable(tty_formatter):
            tty_formatter(payload)
        else:
            sys.stdout.write(json.dumps(payload, indent=2) + "\n")
