"""Tests for CLI stream purity, POSIX exit codes, and self-correction envelopes."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

CLI_BIN = Path(__file__).resolve().parent.parent / "bin" / "ep"


class TestCLIEnvelope(unittest.TestCase):
    def test_cli_usage_error_envelope_on_json_flag(self):
        # Trigger argument error with --json flag
        res = subprocess.run(
            [sys.executable, str(CLI_BIN), "nonexistent-subcommand", "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 2)
        # Verify STDOUT is strictly valid JSON
        data = json.loads(res.stdout)
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["exit_code"], 2)
        self.assertEqual(data["error_type"], "CLI_USAGE_ERROR")
        self.assertIn("usage", data)

    def test_cli_doctor_json_stream_purity(self):
        res = subprocess.run(
            [sys.executable, str(CLI_BIN), "doctor", "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        # Parse STDOUT to guarantee zero ANSI escapes or log pollution
        data = json.loads(res.stdout)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["exit_code"], 0)
        self.assertIn("scanned_files", data)

    def test_cli_version_flag(self):
        res = subprocess.run(
            [sys.executable, str(CLI_BIN), "--version"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("ep", res.stdout)
        self.assertIn("epistex", res.stdout)


if __name__ == "__main__":
    unittest.main()
