"""S3-compatible object storage provider with standard SigV4 and zero third-party deps."""

import datetime
import hashlib
import hmac
import mimetypes
import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Tuple
from config.cloud import (
    S3_ENDPOINT_URL,
    S3_BUCKET_NAME,
    S3_REGION,
    S3_ACCESS_KEY_ID,
    S3_SECRET_ACCESS_KEY,
    CLOUD_AUTH_MODE,
)
from src.contracts.asset_storage import AssetDescriptor, AssetStorageInterface
from src.contracts.secret_provider import SecretProviderInterface
from src.core.errors import VaultError


def _sign(key: bytes, msg: str) -> bytes:
    """Compute HMAC-SHA256 signature."""
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _get_signature_key(key: str, date_stamp: str, region_name: str, service_name: str) -> bytes:
    """Generate AWS SigV4 derived signing key."""
    k_date = _sign(("AWS4" + key).encode("utf-8"), date_stamp)
    k_region = _sign(k_date, region_name)
    k_service = _sign(k_region, service_name)
    return _sign(k_service, "aws4_request")


def _resolve_s3_credentials(
    auth_mode: str,
    secret_provider: Optional[SecretProviderInterface],
    endpoint_url: str,
    bucket: str,
    region: str,
    access_key: Optional[str],
    secret_key: Optional[str],
) -> Tuple[str, str, str, str, str]:
    """Resolve S3 configuration via pure env or pure hermetic secret injection."""
    mode = auth_mode.lower()

    if mode == "hermetic":
        if not secret_provider:
            raise VaultError("Hermetic cloud auth requested but no SecretProvider was provided.", backend="s3")
        ak = access_key or secret_provider.get_secret("AWS_ACCESS_KEY_ID") or ""
        sk = secret_key or secret_provider.get_secret("AWS_SECRET_ACCESS_KEY") or ""
        ep = secret_provider.get_secret("S3_ENDPOINT_URL") or endpoint_url
        bk = secret_provider.get_secret("S3_BUCKET_NAME") or bucket
        rg = secret_provider.get_secret("S3_REGION") or region
        if not ak or not sk:
            raise VaultError("Hermetic injection missing AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY.", backend="s3")
        return ep.rstrip("/"), bk, rg, ak, sk

    if mode == "env":
        ak = access_key or os.getenv("AWS_ACCESS_KEY_ID", "")
        sk = secret_key or os.getenv("AWS_SECRET_ACCESS_KEY", "")
        ep = os.getenv("S3_ENDPOINT_URL", endpoint_url)
        bk = os.getenv("S3_BUCKET_NAME", bucket)
        rg = os.getenv("S3_REGION", region)
        return ep.rstrip("/"), bk, rg, ak, sk

    # Mode: auto (try secret provider first, fall back to host env)
    ak = access_key or (secret_provider.get_secret("AWS_ACCESS_KEY_ID") if secret_provider else None) or os.getenv("AWS_ACCESS_KEY_ID", "")
    sk = secret_key or (secret_provider.get_secret("AWS_SECRET_ACCESS_KEY") if secret_provider else None) or os.getenv("AWS_SECRET_ACCESS_KEY", "")
    ep = (secret_provider.get_secret("S3_ENDPOINT_URL") if secret_provider else None) or os.getenv("S3_ENDPOINT_URL", endpoint_url)
    bk = (secret_provider.get_secret("S3_BUCKET_NAME") if secret_provider else None) or os.getenv("S3_BUCKET_NAME", bucket)
    rg = (secret_provider.get_secret("S3_REGION") if secret_provider else None) or os.getenv("S3_REGION", region)
    return ep.rstrip("/"), bk, rg, ak, sk


class S3CompatibleAssetProvider(AssetStorageInterface):
    """S3-compatible cloud storage provider using pure Python Standard Library REST & SigV4."""

    def __init__(
        self,
        endpoint_url: str = S3_ENDPOINT_URL,
        bucket: str = S3_BUCKET_NAME,
        region: str = S3_REGION,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        auth_mode: str = CLOUD_AUTH_MODE,
        secret_provider: Optional[SecretProviderInterface] = None,
    ) -> None:
        self.auth_mode = auth_mode
        self.secret_provider = secret_provider
        self.endpoint_url, self.bucket, self.region, self.access_key, self.secret_key = _resolve_s3_credentials(
            auth_mode, secret_provider, endpoint_url, bucket, region, access_key, secret_key
        )

    def _build_url(self, remote_key: str) -> str:
        """Construct endpoint URL for bucket and object key."""
        clean_key = remote_key.lstrip("/")
        return f"{self.endpoint_url}/{self.bucket}/{clean_key}"

    def _build_auth_headers(self, method: str, url: str, payload_hash: str) -> Dict[str, str]:
        """Compute standard SigV4 authorization headers."""
        if not self.access_key or not self.secret_key:
            raise VaultError("AWS S3 credentials missing (access_key or secret_key).", backend="s3")

        parsed = urllib.parse.urlparse(url)
        now = datetime.datetime.now(datetime.timezone.utc)
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = now.strftime("%Y%m%d")

        canonical_uri = parsed.path
        canonical_headers = f"host:{parsed.netloc}\nx-amz-content-sha256:{payload_hash}\nx-amz-date:{amz_date}\n"
        signed_headers = "host;x-amz-content-sha256;x-amz-date"
        canonical_request = f"{method}\n{canonical_uri}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}"

        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{self.region}/s3/aws4_request"
        string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

        signing_key = _get_signature_key(self.secret_key, date_stamp, self.region, "s3")
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        auth_header = f"{algorithm} Credential={self.access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        return {
            "Host": parsed.netloc,
            "x-amz-date": amz_date,
            "x-amz-content-sha256": payload_hash,
            "Authorization": auth_header,
        }

    def upload(
        self,
        local_path: Path,
        remote_key: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> AssetDescriptor:
        """Upload file to S3 bucket via standard HTTP PUT."""
        data = local_path.read_bytes()
        payload_hash = hashlib.sha256(data).hexdigest()
        url = self._build_url(remote_key)
        headers = self._build_auth_headers("PUT", url, payload_hash)

        mime, _ = mimetypes.guess_type(str(local_path))
        content_type = mime or "application/octet-stream"
        headers["Content-Type"] = content_type

        req = urllib.request.Request(url, data=data, headers=headers, method="PUT")
        with urllib.request.urlopen(req, timeout=30.0) as resp:
            if resp.status not in (200, 204):
                raise IOError(f"S3 upload failed with HTTP status {resp.status}")

        return AssetDescriptor(
            remote_key=remote_key,
            sha256=payload_hash,
            size_bytes=len(data),
            mime_type=content_type,
            backend="s3",
            url=url,
            local_path=str(local_path),
            sync_status="synced",
        )

    def download(self, remote_key: str, target_path: Path) -> Path:
        """Download remote S3 asset via HTTP GET."""
        url = self._build_url(remote_key)
        headers = self._build_auth_headers("GET", url, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

        req = urllib.request.Request(url, headers=headers, method="GET")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(req, timeout=60.0) as resp, open(target_path, "wb") as f:
            while chunk := resp.read(65536):
                f.write(chunk)
        return target_path

    def exists(self, remote_key: str) -> bool:
        """Check remote key existence via HTTP HEAD."""
        url = self._build_url(remote_key)
        try:
            headers = self._build_auth_headers("HEAD", url, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
            req = urllib.request.Request(url, headers=headers, method="HEAD")
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def get_url(self, remote_key: str, expires_in: int = 3600) -> str:
        """Get public or direct endpoint URL for the object."""
        return self._build_url(remote_key)

    def get_backend_name(self) -> str:
        return "s3"
