#Owner::ANIKET::ANHOTRA = MR.Panda
"""Private S3-compatible immutable original-byte storage with checksum verification."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from functools import lru_cache

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from backend.app.services.file_integrity_service import MAX_ORIGINAL_BYTES


class StorageUnavailable(Exception):
    """Untrusted object could not be safely persisted or verified."""


@dataclass(frozen=True)
class StorageConfig:
    """Scoped object-storage connection with no public bucket access."""

    bucket: str
    endpoint: str
    access_key: str
    secret_key: str


def load_storage_config() -> StorageConfig:
    """Require explicit private object-storage credentials on use."""

    endpoint = os.getenv("SITEPAY_OBJECT_STORAGE_ENDPOINT", "")
    bucket = os.getenv("SITEPAY_OBJECT_STORAGE_BUCKET", "")
    access_key = os.getenv("SITEPAY_OBJECT_STORAGE_ACCESS_KEY", "")
    secret_key = os.getenv("SITEPAY_OBJECT_STORAGE_SECRET_KEY", "")
    if not all((endpoint, bucket, access_key, secret_key)):
        raise StorageUnavailable("Private evidence storage is not configured")
    if not endpoint.startswith(("http://", "https://")):
        raise StorageUnavailable("Invalid private object-storage endpoint")
    environment = os.getenv("SITEPAY_ENVIRONMENT", "development")
    if environment in {"staging", "production"} and not endpoint.startswith("https://"):
        raise StorageUnavailable("TLS is required for production storage")
    return StorageConfig(bucket, endpoint, access_key, secret_key)


@lru_cache(maxsize=1)
def get_storage_client() -> object:
    """Create a bounded private S3 client without global credentials fallbacks."""

    configuration = load_storage_config()
    return boto3.client(
        "s3",
        endpoint_url=configuration.endpoint,
        aws_access_key_id=configuration.access_key,
        aws_secret_access_key=configuration.secret_key,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
            connect_timeout=3,
            read_timeout=10,
            retries={"max_attempts": 2},
        ),
    )


def original_object_key(organization_id: str, project_id: str, checksum: str) -> str:
    """Generate a tenant- and project-scoped, content-addressed object key."""

    return f"originals/{organization_id}/{project_id}/sha256/{checksum}"


def read_original(object_key: str, expected_checksum: str, expected_size: int) -> bytes:
    """Read and verify original bytes before releasing them to an authorised API."""

    try:
        response = get_storage_client().get_object(
            Bucket=load_storage_config().bucket, Key=object_key
        )
        body = response["Body"]
        try:
            content = body.read(MAX_ORIGINAL_BYTES + 1)
        finally:
            body.close()
    except (BotoCoreError, ClientError, OSError) as error:
        raise StorageUnavailable("Original evidence is unavailable") from error
    if (
        len(content) != expected_size
        or len(content) > MAX_ORIGINAL_BYTES
        or hashlib.sha256(content).hexdigest() != expected_checksum
    ):
        raise StorageUnavailable("Stored original failed integrity verification")
    return content


def store_original(
    content: bytes, *, organization_id: str, project_id: str,
    checksum: str, content_type: str,
) -> str:
    """Write once with an S3 conditional PUT, then verify the exact original.

    Never overwrite a matching key and never delete an original on DB failure.
    """
    if hashlib.sha256(content).hexdigest() != checksum:
        raise StorageUnavailable("Original checksum differs from validated bytes")
    key = original_object_key(organization_id, project_id, checksum)
    try:
        get_storage_client().put_object(
            Bucket=load_storage_config().bucket,
            Key=key,
            Body=content,
            ContentType=content_type,
            Metadata={"sha256": checksum},
            IfNoneMatch="*",
        )
    except ClientError as error:
        code = str(error.response.get("Error", {}).get("Code", ""))
        if code not in {"PreconditionFailed", "412", "ConditionalRequestConflict", "409"}:
            raise StorageUnavailable("Could not persist original evidence") from error
    except BotoCoreError as error:
        raise StorageUnavailable("Could not persist original evidence") from error
    persisted = read_original(key, checksum, len(content))
    if persisted != content:
        raise StorageUnavailable("Stored original is not equal to submitted bytes")
    return key
