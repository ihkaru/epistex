"""Cloud and object storage configuration (opt-in, zero vendor lock-in)."""

import os
from pathlib import Path
from config.app import STORAGE_DIR

# Opt-in cloud storage backend: "local" (default offline), "s3", or "auto"
CLOUD_STORAGE_BACKEND = os.getenv("EPISTEX_CLOUD_STORAGE", "local").lower()

# Local asset directory (fallback & caching)
LOCAL_ASSET_DIR = Path(os.getenv("EPISTEX_LOCAL_ASSET_DIR", str(STORAGE_DIR / "assets")))

# S3-compatible configuration (AWS S3, MinIO, Cloudflare R2, Coolify S3, Ceph, Backblaze)
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "https://s3.amazonaws.com")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "epistex-assets")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
S3_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
S3_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")

# Default max upload chunk size (5MB for streaming)
DEFAULT_CHUNK_SIZE = 5 * 1024 * 1024

# Cloud authentication mode: "env" (pure environment variables), "hermetic" (runtime secret injection), or "auto"
CLOUD_AUTH_MODE = os.getenv("EPISTEX_CLOUD_AUTH", "auto").lower()

