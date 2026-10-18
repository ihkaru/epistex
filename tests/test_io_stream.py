"""Tests for streaming frontmatter reader and atomic writes."""

import unittest
from pathlib import Path
import tempfile
from src.core.io_stream import read_frontmatter_streaming, atomic_write_text


class TestIOStream(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_read_frontmatter_streaming_early_exit(self):
        doc = self.root / "sample.md"
        # 10 lines of frontmatter + 500 lines of body
        body = "\n".join([f"Line {i} of huge markdown body" for i in range(500)])
        content = f"---\ntitle: Fast Stream\nstatus: active\ncategory: runbook\nowner: @ops\n---\n\n{body}"
        doc.write_text(content, encoding="utf-8")

        meta, end_line, raw = read_frontmatter_streaming(doc)
        self.assertEqual(meta.get("title"), "Fast Stream")
        self.assertEqual(meta.get("status"), "active")
        self.assertEqual(meta.get("category"), "runbook")
        self.assertEqual(meta.get("owner"), "@ops")
        self.assertEqual(end_line, 6)

    def test_atomic_write_text(self):
        target = self.root / "nested" / "doc.txt"
        atomic_write_text(target, "Hello Atomic World")
        self.assertTrue(target.exists())
        self.assertEqual(target.read_text(encoding="utf-8"), "Hello Atomic World")


if __name__ == "__main__":
    unittest.main()
