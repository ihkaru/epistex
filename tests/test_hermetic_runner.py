"""Tests for hermetic code runner, environment stripping, and timeout handling."""

import sys
import unittest
from src.providers.runner.hermetic_runner import HermeticCodeRunner
from src.providers.secrets.memory_provider import MemorySecretProvider


class TestHermeticRunner(unittest.TestCase):
    def test_environment_stripping_and_injection(self):
        secrets = {"API_TOKEN": "token_xyz", "APP_ENV": "production"}
        provider = MemorySecretProvider(secrets)
        runner = HermeticCodeRunner(
            secret_provider=provider,
            safe_env_vars={"PATH", "PYTHONPATH"},
        )

        code = "import os; print(os.getenv('API_TOKEN'), os.getenv('APP_ENV'))"
        result = runner.run([sys.executable, "-c", code])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("token_xyz production", result.stdout)
        self.assertEqual(result.injected_secret_count, 2)
        self.assertFalse(result.timed_out)

    def test_dry_run_simulation(self):
        provider = MemorySecretProvider({"SECRET_A": "val_a"})
        runner = HermeticCodeRunner(secret_provider=provider)

        result = runner.run(["python3", "nonexistent.py"], dry_run=True)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("[DRY-RUN]", result.stdout)
        self.assertEqual(result.injected_secret_count, 1)

    def test_timeout_enforcement(self):
        provider = MemorySecretProvider()
        runner = HermeticCodeRunner(secret_provider=provider)

        code = "import time; time.sleep(1.5)"
        result = runner.run([sys.executable, "-c", code], timeout=0.2)
        self.assertTrue(result.timed_out)
        self.assertEqual(result.exit_code, 124)


if __name__ == "__main__":
    unittest.main()
