"""Tests for zero-dependency restricted YAML frontmatter parser."""

import unittest
from src.core.yaml_parser import parse_restricted_yaml


class TestYamlParser(unittest.TestCase):
    def test_parse_scalars(self):
        text = """
        title: "Architecture Decision"
        status: active
        count: 42
        pi: 3.14
        is_active: true
        is_deprecated: false
        empty_field: null
        """
        data = parse_restricted_yaml(text)
        self.assertEqual(data["title"], "Architecture Decision")
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["count"], 42)
        self.assertAlmostEqual(data["pi"], 3.14)
        self.assertTrue(data["is_active"])
        self.assertFalse(data["is_deprecated"])
        self.assertIsNone(data["empty_field"])

    def test_parse_inline_and_block_lists(self):
        text = """
        tags: [architecture, eda, solid]
        deadlines:
          - milestone: Phase 1
            due: 2026-11-01
          - milestone: Phase 2
            due: 2026-12-01
        """
        data = parse_restricted_yaml(text)
        self.assertEqual(data["tags"], ["architecture", "eda", "solid"])
        self.assertEqual(len(data["deadlines"]), 2)
        self.assertEqual(data["deadlines"][0]["milestone"], "Phase 1")
        self.assertEqual(data["deadlines"][0]["due"], "2026-11-01")
        self.assertEqual(data["deadlines"][1]["milestone"], "Phase 2")
        self.assertEqual(data["deadlines"][1]["due"], "2026-12-01")


if __name__ == "__main__":
    unittest.main()
