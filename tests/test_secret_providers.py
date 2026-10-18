"""Tests for secret providers and factory resolution."""

import unittest
from pathlib import Path
import tempfile
from src.providers.secrets.env_provider import EnvSecretProvider
from src.providers.secrets.memory_provider import MemorySecretProvider
from src.providers.secrets.infisical_provider import InfisicalSecretProvider
from src.providers.secrets.factory import create_secret_provider


class TestSecretProviders(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_memory_secret_provider(self):
        provider = MemorySecretProvider({"API_KEY": "secret123", "PORT": "8080"})
        self.assertEqual(provider.get_secret("API_KEY"), "secret123")
        self.assertEqual(provider.get_backend_name(), "memory")

        env = provider.inject_env({"PATH": "/bin"})
        self.assertEqual(env["API_KEY"], "secret123")
        self.assertEqual(env["PATH"], "/bin")

    def test_env_provider_with_local_file(self):
        env_file = self.root / ".env"
        env_file.write_text("DB_HOST=localhost\nDB_PASS=securepass\n# Comment\n", encoding="utf-8")

        provider = EnvSecretProvider(env_file=env_file)
        self.assertEqual(provider.get_secret("DB_HOST"), "localhost")
        self.assertEqual(provider.get_secret("DB_PASS"), "securepass")
        self.assertEqual(provider.get_backend_name(), "env")

    def test_factory_creation(self):
        mem = create_secret_provider("memory")
        self.assertEqual(mem.get_backend_name(), "memory")

        env = create_secret_provider("env")
        self.assertEqual(env.get_backend_name(), "env")


if __name__ == "__main__":
    unittest.main()
