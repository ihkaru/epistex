"""Tests for bounded min-heap schedule queries."""

import unittest
from pathlib import Path
import tempfile
from src.commands.cmd_schedule import run_schedule


class TestSchedule(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        doc1 = self.root / "act1.md"
        doc1.write_text(
            """---
title: Activity 1
status: active
category: activity
owner: @team
deadlines:
  - milestone: Late Deadline
    due: 2026-12-01
  - milestone: Early Deadline
    due: 2026-10-20
---
# Act 1
""",
            encoding="utf-8",
        )

        doc2 = self.root / "act2.md"
        doc2.write_text(
            """---
title: Activity 2
status: active
category: activity
owner: @team
deadlines:
  - milestone: Mid Deadline
    due: 2026-11-15
---
# Act 2
""",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_schedule_sorted_by_due_date_min_heap(self):
        code, payload = run_schedule(base_dir=self.root, limit=10)
        self.assertEqual(code, 0)
        schedules = payload["schedules"]
        self.assertEqual(len(schedules), 3)

        # Earliest first
        self.assertEqual(schedules[0]["due"], "2026-10-20")
        self.assertEqual(schedules[0]["milestone"], "Early Deadline")
        self.assertEqual(schedules[1]["due"], "2026-11-15")
        self.assertEqual(schedules[2]["due"], "2026-12-01")

    def test_schedule_limit_enforced(self):
        code, payload = run_schedule(base_dir=self.root, limit=2)
        self.assertEqual(code, 0)
        self.assertEqual(len(payload["schedules"]), 2)
        self.assertEqual(payload["schedules"][0]["due"], "2026-10-20")
        self.assertEqual(payload["schedules"][1]["due"], "2026-11-15")


if __name__ == "__main__":
    unittest.main()
