"""Tests for local and S3 asset storage providers."""

import unittest
from pathlib import Path
import tempfile
from src.providers.storage.local_provider import LocalAssetProvider, compute_file_sha256
from src.providers.storage.s3_provider import S3CompatibleAssetProvider
from src.providers.storage.factory import create_asset_storage


class TestAssetStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_local_asset_provider_upload_and_download(self):
        storage_dir = self.root / "storage_assets"
        provider = LocalAssetProvider(base_dir=storage_dir)

        # Create sample binary file
        src = self.root / "sample.pdf"
        src.write_bytes(b"%PDF-1.4 sample binary payload")

        desc = provider.upload(src, "docs/sample.pdf")
        self.assertEqual(desc.remote_key, "docs/sample.pdf")
        self.assertEqual(desc.backend, "local")
        self.assertEqual(desc.size_bytes, src.stat().st_size)
        self.assertTrue(provider.exists("docs/sample.pdf"))

        # Download to different location
        dest = self.root / "downloaded.pdf"
        provider.download("docs/sample.pdf", dest)
        self.assertTrue(dest.exists())
        self.assertEqual(compute_file_sha256(dest), desc.sha256)

    def test_s3_url_and_auth_headers_generation(self):
        provider = S3CompatibleAssetProvider(
            endpoint_url="https://s3.example.com",
            bucket="test-bucket",
            region="us-east-1",
            access_key="MOCK_ACCESS_KEY",
            secret_key="MOCK_SECRET_KEY",
        )
        url = provider.get_url("images/diagram.png")
        self.assertEqual(url, "https://s3.example.com/test-bucket/images/diagram.png")

        headers = provider._build_auth_headers("PUT", url, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        self.assertIn("Authorization", headers)
        self.assertIn("AWS4-HMAC-SHA256", headers["Authorization"])
        self.assertEqual(headers["Host"], "s3.example.com")

    def test_factory_defaults_to_local_opt_in(self):
        default_storage = create_asset_storage()
        self.assertEqual(default_storage.get_backend_name(), "local")

        s3_storage = create_asset_storage("s3")
        self.assertEqual(s3_storage.get_backend_name(), "s3")


if __name__ == "__main__":
    unittest.main()
