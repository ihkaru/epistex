"""Tests for kb doctor health audit engine."""

import unittest
from pathlib import Path
import tempfile
from src.commands.cmd_doctor import run_doctor
from src.core.schema_validator import SchemaValidator
from config.app import EX_OK, EX_DATAERR


class TestDoctor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_schema_validator_catches_invalid_status(self):
        validator = SchemaValidator()
        frontmatter = {
            "title": "Invalid Status Doc",
            "status": "wrong-status",
            "category": "runbook",
            "owner": "@team",
        }
        issues = validator.validate_document(Path("test.md"), frontmatter, 6)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].error_type, "INVALID_STATUS")
        self.assertIn("Change 'status: wrong-status' to one of:", issues[0].fix_hint)

    def test_schema_validator_catches_missing_required_field(self):
        validator = SchemaValidator()
        frontmatter = {
            "title": "Incomplete Doc",
            "status": "draft",
            # missing category and owner
        }
        issues = validator.validate_document(Path("test.md"), frontmatter, 4)
        field_names = [issue.field_name for issue in issues]
        self.assertIn("category", field_names)
        self.assertIn("owner", field_names)

    def test_doctor_on_healthy_directory(self):
        valid_doc = self.root / "valid.md"
        valid_doc.write_text(
            "---\ntitle: Healthy\nstatus: active\ncategory: runbook\nowner: @ops\n---\n# OK",
            encoding="utf-8",
        )
        code, payload = run_doctor(base_dir=self.root)
        self.assertEqual(code, EX_OK)
        self.assertEqual(payload["total_issues"], 0)


if __name__ == "__main__":
    unittest.main()
