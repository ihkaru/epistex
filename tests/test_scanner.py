"""Tests for pruned directory scanner and inverted file index."""

import unittest
from pathlib import Path
import tempfile
from src.core.scanner import scan_markdown_files, build_inverted_file_index


class TestScanner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Create sample structure
        (self.root / "knowledge" / "engineering").mkdir(parents=True)
        (self.root / "knowledge" / "engineering" / "doc1.md").write_text("# Doc 1", encoding="utf-8")
        (self.root / "knowledge" / "doc2.md").write_text("# Doc 2", encoding="utf-8")
        (self.root / "knowledge" / "asset.png").write_text("fake-image", encoding="utf-8")

        # Create ignored dirs
        (self.root / ".git").mkdir()
        (self.root / ".git" / "hidden.md").write_text("# Git Hidden", encoding="utf-8")
        (self.root / "node_modules").mkdir()
        (self.root / "node_modules" / "ignored.md").write_text("# Node Ignored", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_scan_markdown_files_pruning(self):
        md_files = list(scan_markdown_files(self.root))
        filenames = {p.name for p in md_files}
        self.assertIn("doc1.md", filenames)
        self.assertIn("doc2.md", filenames)
        self.assertNotIn("hidden.md", filenames)
        self.assertNotIn("ignored.md", filenames)
        self.assertNotIn("asset.png", filenames)

    def test_build_inverted_file_index(self):
        index = build_inverted_file_index(self.root)
        self.assertIn("knowledge/engineering/doc1.md", index)
        self.assertIn("knowledge/doc2.md", index)
        self.assertIn("knowledge/asset.png", index)
        # Verify ignored dirs are pruned from index
        self.assertNotIn(".git/hidden.md", index)
        self.assertNotIn("node_modules/ignored.md", index)


if __name__ == "__main__":
    unittest.main()
