"""Tests for repository initialization and specialization installer command."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.commands.cmd_init import run_init
from src.events.dispatcher import EventDispatcher


CLI_BIN = Path(__file__).resolve().parent.parent / "bin" / "ep"


class TestInitCommand(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Scaffold mock repository structure
        (self.root / "config").mkdir(parents=True)
        (self.root / "config" / "app.py").write_text(
            'APP_NAME = "epistex"\nAPP_DESCRIPTION = "Starter Kit"\nIS_STARTER_KIT = True\n',
            encoding="utf-8",
        )
        (self.root / ".env.example").write_text("SAMPLE_KEY=sample_val\n", encoding="utf-8")

        docs_dir = self.root / "docs"
        docs_dir.mkdir(parents=True)
        (docs_dir / "RELEASING.md").write_text("# Upstream Releasing Protocol\n", encoding="utf-8")

        adr_dir = self.root / "knowledge" / "engineering" / "adr"
        adr_dir.mkdir(parents=True)
        (adr_dir / "ADR-001-event-driven-architecture.md").write_text("# ADR Sample\n", encoding="utf-8")

        act_dir = self.root / "knowledge" / "activities" / "quarterly-audit" / "2026-Q4"
        act_dir.mkdir(parents=True)
        (act_dir / "README.md").write_text("# Audit Sample\n", encoding="utf-8")

        (self.root / "README.md").write_text(
            "# Epistex\n\n"
            "> [!IMPORTANT]\n"
            "> **Starter Kit Specialization Notice (Replace Once Adopted)**:\n"
            "> Please specialize this repository.\n\n"
            "---\n\n"
            "## Key Highlights\n"
            "- High performance\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init_dry_run_simulation(self):
        code, payload = run_init(
            name="Acme-KB",
            description="Acme Systems Knowledge Base",
            owner="@acme",
            clean_samples=True,
            clean_notice=True,
            dry_run=True,
            interactive=False,
            root_dir=self.root,
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["name"], "Acme-KB")
        self.assertTrue(payload["specialization_notice_cleaned"])
        self.assertEqual(len(payload["samples_pruned"]), 2)

        # Verify disk remains untouched
        app_content = (self.root / "config" / "app.py").read_text(encoding="utf-8")
        self.assertIn('APP_NAME = "epistex"', app_content)
        self.assertFalse((self.root / ".env").exists())

    def test_init_execution_modifies_files_and_cleans_samples(self):
        dispatched_events = []
        dispatcher = EventDispatcher()
        dispatcher.subscribe("repository.initialized", lambda evt: dispatched_events.append(evt))

        code, payload = run_init(
            name="BankData-KB",
            description="Core Banking Knowledge Base",
            owner="@banking-arch",
            clean_samples=True,
            clean_notice=True,
            dry_run=False,
            interactive=False,
            root_dir=self.root,
            dispatcher=dispatcher,
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "ok")

        # Verify config update
        app_content = (self.root / "config" / "app.py").read_text(encoding="utf-8")
        self.assertIn('APP_NAME = "BankData-KB"', app_content)
        self.assertIn('APP_DESCRIPTION = "Core Banking Knowledge Base"', app_content)
        self.assertIn('IS_STARTER_KIT = False', app_content)
        self.assertFalse(payload["starter_kit_mode"])

        # Verify .env copied
        self.assertTrue((self.root / ".env").exists())
        self.assertIn("SAMPLE_KEY=sample_val", (self.root / ".env").read_text(encoding="utf-8"))

        # Verify samples and maintainer docs pruned
        adr_file = self.root / "knowledge" / "engineering" / "adr" / "ADR-001-event-driven-architecture.md"
        self.assertFalse(adr_file.exists())
        releasing_file = self.root / "docs" / "RELEASING.md"
        self.assertFalse(releasing_file.exists())
        self.assertIn("docs/RELEASING.md", payload["maintainer_docs_pruned"])

        # Verify README notice replaced
        readme_content = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("Starter Kit Specialization Notice", readme_content)
        self.assertIn("Active Knowledge Base**: Initialized for **BankData-KB", readme_content)

        # Verify event dispatched
        self.assertEqual(len(dispatched_events), 1)
        self.assertEqual(dispatched_events[0].payload["name"], "BankData-KB")

        # Verify githooks_activated is present in payload
        self.assertIn("githooks_activated", payload)

    def test_init_cli_stream_purity_on_json(self):
        res = subprocess.run(
            [sys.executable, str(CLI_BIN), "init", "--dry-run", "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["action"], "repository_initialized")


if __name__ == "__main__":
    unittest.main()
