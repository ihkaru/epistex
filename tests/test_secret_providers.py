"""Tests for secret providers and factory resolution."""

import unittest
from pathlib import Path
import tempfile
from src.providers.secrets.env_provider import EnvSecretProvider
from src.providers.secrets.memory_provider import MemorySecretProvider
from src.providers.secrets.infisical_provider import (
    InfisicalSecretProvider,
    parse_infisical_payload,
)
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

    def test_parse_infisical_payload_formats(self):
        # Format 1: infisical export list with key & value
        data_export = [
            {"key": "API_KEY", "value": "secret1"},
            {"key": "PORT", "value": "9000"},
        ]
        parsed_export = parse_infisical_payload(data_export)
        self.assertEqual(parsed_export, {"API_KEY": "secret1", "PORT": "9000"})

        # Format 2: infisical secrets list with secretKey & secretValue
        data_secrets = [
            {"secretKey": "TOKEN", "secretValue": "token_abc"},
        ]
        parsed_secrets = parse_infisical_payload(data_secrets)
        self.assertEqual(parsed_secrets, {"TOKEN": "token_abc"})

        # Format 3: simple dictionary
        data_dict = {"HOST": "127.0.0.1", "USER": "root"}
        parsed_dict = parse_infisical_payload(data_dict)
        self.assertEqual(parsed_dict, {"HOST": "127.0.0.1", "USER": "root"})

        # Format 4: non-dict / non-list safe handling
        self.assertEqual(parse_infisical_payload("invalid"), {})
        self.assertEqual(parse_infisical_payload([None, "string", 123]), {})

    def test_infisical_provider_properties(self):
        provider = InfisicalSecretProvider(fallback_provider=MemorySecretProvider({"FOO": "bar"}))
        self.assertEqual(provider.get_backend_name(), "infisical")


if __name__ == "__main__":
    unittest.main()
