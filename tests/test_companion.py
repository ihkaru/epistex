"""Tests for Git-native companion markdown documents."""

import unittest
from pathlib import Path
import tempfile
from src.contracts.asset_storage import AssetDescriptor
from src.core.companion import (
    format_companion_markdown,
    write_companion_file,
    parse_companion_metadata,
)
from src.core.io_stream import read_frontmatter_streaming


class TestCompanion(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_format_and_parse_companion(self):
        desc = AssetDescriptor(
            remote_key="engineering/arch.pdf",
            sha256="abc123sha",
            size_bytes=1024,
            mime_type="application/pdf",
            backend="s3",
            sync_status="remote",
        )
        target = self.root / "arch.md"
        write_companion_file(target, desc, title="Architecture Spec", owner="@infra")

        self.assertTrue(target.exists())
        meta, end_line, raw = read_frontmatter_streaming(target)
        self.assertEqual(meta["title"], "Architecture Spec")
        self.assertEqual(meta["category"], "asset-companion")

        parsed_asset = parse_companion_metadata(meta)
        self.assertIsNotNone(parsed_asset)
        self.assertEqual(parsed_asset["remote_key"], "engineering/arch.pdf")
        self.assertEqual(parsed_asset["sha256"], "abc123sha")
        self.assertEqual(parsed_asset["size_bytes"], 1024)


if __name__ == "__main__":
    unittest.main()
