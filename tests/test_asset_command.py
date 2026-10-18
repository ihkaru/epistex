"""Tests for asset management CLI subcommands."""

import unittest
from pathlib import Path
import tempfile
from src.commands.cmd_asset import (
    run_asset_push,
    run_asset_pull,
    run_asset_check,
    run_asset_list,
)
from src.commands.cmd_doctor import run_doctor
from src.providers.storage.local_provider import LocalAssetProvider


class TestAssetCommand(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.storage_dir = self.root / "storage_assets"
        self.knowledge_dir = self.root / "knowledge"
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.storage = LocalAssetProvider(base_dir=self.storage_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_push_pull_check_cycle(self):
        src_bin = self.root / "data.bin"
        src_bin.write_bytes(b"binary payload 12345")

        comp_rel = "assets/data.md"
        # 1. Push
        code, push_res = run_asset_push(
            local_file=str(src_bin),
            remote_key="binaries/data.bin",
            companion_path=comp_rel,
            title="Binary Data Asset",
            storage=self.storage,
            base_dir=self.knowledge_dir,
        )
        self.assertEqual(code, 0)
        self.assertEqual(push_res["remote_key"], "binaries/data.bin")


        # 2. Check
        code, check_res = run_asset_check("binaries/data.bin", storage=self.storage)
        self.assertEqual(code, 0)
        self.assertTrue(check_res["exists"])

        # 3. Pull
        dest_bin = self.root / "restored.bin"
        code, pull_res = run_asset_pull(
            remote_key="binaries/data.bin",
            target_path=str(dest_bin),
            storage=self.storage,
        )
        self.assertEqual(code, 0)
        self.assertTrue(dest_bin.exists())
        self.assertEqual(dest_bin.read_bytes(), b"binary payload 12345")

    def test_doctor_detects_missing_cloud_asset_when_checked(self):
        # Create companion pointing to non-existent remote asset
        broken_comp = self.knowledge_dir / "broken.md"
        broken_comp.write_text(
            """---
title: Broken Asset
status: active
category: asset-companion
owner: @team
asset:
  remote_key: nonexistent/ghost.pdf
  sha256: fakehash
  size_bytes: 500
  storage_backend: local
---
# Broken
""",
            encoding="utf-8",
        )

        # Normal doctor run doesn't check cloud assets
        code, res = run_doctor(base_dir=self.knowledge_dir, check_assets=False)
        self.assertEqual(code, 0)
        self.assertEqual(len(res["asset_issues"]), 0)

        # Opt-in doctor run with check_assets=True detects missing remote asset!
        code, res = run_doctor(
            base_dir=self.knowledge_dir,
            check_assets=True,
            asset_storage=self.storage,
        )
        self.assertNotEqual(code, 0)
        self.assertEqual(len(res["asset_issues"]), 1)
        self.assertEqual(res["asset_issues"][0]["remote_key"], "nonexistent/ghost.pdf")


if __name__ == "__main__":
    unittest.main()
