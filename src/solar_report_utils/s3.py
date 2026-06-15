"""Shared S3 base client for the solar report builders.

Provides the common boto3 setup (with timeouts + bounded retries) and generic
object primitives. Each builder subclasses ``BaseS3Client`` and adds its own
domain-specific download/upload methods on top of these primitives.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import boto3
from botocore.config import Config

from .exceptions import S3DownloadError, S3UploadError

logger = logging.getLogger(__name__)


def parse_s3_uri(uri: str) -> tuple[str, str]:
    """Split an ``s3://bucket/key`` URI into ``(bucket, key)``."""
    if not uri.startswith("s3://"):
        raise ValueError(f"Not an S3 URI: {uri!r}")
    without_scheme = uri[len("s3://") :]
    bucket, _, key = without_scheme.partition("/")
    if not bucket:
        raise ValueError(f"S3 URI missing bucket: {uri!r}")
    return bucket, key


class BaseS3Client:
    """Generic S3 operations shared by every report builder."""

    def __init__(self, region: str = "us-east-2"):
        self.region = region
        # Explicit timeouts + bounded retries prevent thundering-herd hangs
        # when many transfers run concurrently.
        self.s3 = boto3.client(
            "s3",
            region_name=self.region,
            config=Config(
                connect_timeout=10,
                read_timeout=60,
                retries={"max_attempts": 3},
            ),
        )
        logger.info("Initialized S3 client for region %s", self.region)

    def download_file(self, bucket: str, key: str, local_path: Path) -> Path:
        """Download a single object to ``local_path``."""
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.s3.download_file(bucket, key, str(local_path))
        except Exception as exc:  # noqa: BLE001 - re-raised as domain error
            raise S3DownloadError(f"Failed to download s3://{bucket}/{key}: {exc}") from exc
        return local_path

    def upload_file(self, local_path: Path, bucket: str, key: str) -> str:
        """Upload ``local_path`` and return its ``s3://`` URI."""
        try:
            self.s3.upload_file(str(local_path), bucket, key)
        except Exception as exc:  # noqa: BLE001 - re-raised as domain error
            raise S3UploadError(f"Failed to upload to s3://{bucket}/{key}: {exc}") from exc
        return f"s3://{bucket}/{key}"

    def list_objects(self, bucket: str, prefix: str) -> list[str]:
        """Return every object key under ``prefix`` (handles pagination)."""
        keys: list[str] = []
        paginator = self.s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])
        return keys

    def download_prefix(
        self, bucket: str, prefix: str, local_dir: Path, suffixes: Optional[tuple[str, ...]] = None
    ) -> list[Path]:
        """Download every object under ``prefix`` into ``local_dir``.

        ``suffixes`` optionally restricts to keys ending with one of them
        (case-insensitive). Returns the list of local paths written.
        """
        local_dir = Path(local_dir)
        local_dir.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        for key in self.list_objects(bucket, prefix):
            if suffixes and not key.lower().endswith(tuple(s.lower() for s in suffixes)):
                continue
            dest = local_dir / Path(key).name
            self.download_file(bucket, key, dest)
            written.append(dest)
        return written
