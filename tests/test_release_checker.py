"""Tests for deterministic release readiness and anti-poisoning engine."""

import unittest
from pathlib import Path
from src.core.release_checker import (
    audit_release_readiness,
    _determine_bump_type,
)
from src.commands.cmd_doctor import run_doctor


class TestReleaseChecker(unittest.TestCase):
    def test_downstream_mode_suppresses_release(self):
        root = Path(__file__).resolve().parent.parent
        res = audit_release_readiness(root, is_starter_kit=False)
        self.assertFalse(res["release_required"])
        self.assertEqual(res["mode"], "downstream_operational")
        self.assertIn("Downstream operational mode", res["reason"])

    def test_bump_type_determination_patch(self):
        commits = [
            {"hash": "abc1", "message": "fix: correct error envelope exit code"},
            {"hash": "abc2", "message": "perf: optimize inverted index scanning"},
        ]
        self.assertEqual(_determine_bump_type(commits), "patch")

    def test_bump_type_determination_minor(self):
        commits = [
            {"hash": "abc1", "message": "fix: typo in doctor output"},
            {"hash": "abc2", "message": "feat(cli): add ep init specialization installer"},
        ]
        self.assertEqual(_determine_bump_type(commits), "minor")

    def test_bump_type_determination_major_breaking_change(self):
        commits = [
            {"hash": "abc1", "message": "feat: restructure interfaces\n\nBREAKING CHANGE: contract updated"},
        ]
        self.assertEqual(_determine_bump_type(commits), "major")

    def test_bump_type_determination_major_exclamation(self):
        commits = [
            {"hash": "abc1", "message": "feat!: drop deprecated legacy flags"},
        ]
        self.assertEqual(_determine_bump_type(commits), "major")

    def test_doctor_integration_with_check_release(self):
        code, payload = run_doctor(check_release=True)
        self.assertIn("release_readiness", payload)
        readiness = payload["release_readiness"]
        self.assertIn("release_required", readiness)
        self.assertIn("mode", readiness)


if __name__ == "__main__":
    unittest.main()
