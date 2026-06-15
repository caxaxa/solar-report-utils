import logging
from pathlib import Path

import boto3
import pytest
from moto import mock_aws

from solar_report_utils import (
    BaseReportSettings,
    BaseS3Client,
    ProcessingError,
    S3DownloadError,
    S3UploadError,
    get_bucket_suffix,
    parse_s3_uri,
    setup_logging,
)


class TestExceptions:
    def test_hierarchy(self):
        assert issubclass(S3DownloadError, ProcessingError)
        assert issubclass(S3UploadError, ProcessingError)


class TestParseS3Uri:
    def test_splits_bucket_and_key(self):
        assert parse_s3_uri("s3://my-bucket/path/to/obj.tif") == ("my-bucket", "path/to/obj.tif")

    def test_bucket_only(self):
        assert parse_s3_uri("s3://my-bucket") == ("my-bucket", "")

    def test_rejects_non_s3(self):
        with pytest.raises(ValueError):
            parse_s3_uri("https://example.com/x")


class TestBucketSuffix:
    def test_prod_default(self, monkeypatch):
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        assert get_bucket_suffix() == "prod"

    def test_dev(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "dev")
        assert get_bucket_suffix() == "dev"


class TestBaseReportSettings:
    def test_solar_prefix_and_extra_ignored(self, monkeypatch):
        monkeypatch.setenv("SOLAR_AWS_REGION", "eu-west-1")
        monkeypatch.setenv("SOLAR_SOMETHING_UNKNOWN", "x")  # extra=ignore

        class S(BaseReportSettings):
            project_id: str = "p"

        s = S()
        assert s.aws_region == "eu-west-1"
        assert s.project_id == "p"


class TestSetupLogging:
    def test_configures_single_handler(self):
        setup_logging("DEBUG")
        root = logging.getLogger()
        assert root.level == logging.DEBUG
        assert len(root.handlers) == 1


@mock_aws
class TestBaseS3Client:
    def _bucket(self, name="test-bucket"):
        boto3.client("s3", region_name="us-east-2").create_bucket(
            Bucket=name,
            CreateBucketConfiguration={"LocationConstraint": "us-east-2"},
        )
        return name

    def test_upload_then_download(self, tmp_path):
        bucket = self._bucket()
        client = BaseS3Client(region="us-east-2")
        src = tmp_path / "src.txt"
        src.write_text("hello")
        uri = client.upload_file(src, bucket, "k/src.txt")
        assert uri == f"s3://{bucket}/k/src.txt"

        dest = tmp_path / "out" / "got.txt"
        client.download_file(bucket, "k/src.txt", dest)
        assert dest.read_text() == "hello"

    def test_download_missing_raises(self, tmp_path):
        bucket = self._bucket()
        client = BaseS3Client(region="us-east-2")
        with pytest.raises(S3DownloadError):
            client.download_file(bucket, "nope", tmp_path / "x")

    def test_list_and_download_prefix(self, tmp_path):
        bucket = self._bucket()
        client = BaseS3Client(region="us-east-2")
        for i in range(3):
            f = tmp_path / f"f{i}.jpg"
            f.write_text(str(i))
            client.upload_file(f, bucket, f"p/f{i}.jpg")
        client.upload_file(tmp_path / "f0.jpg", bucket, "p/skip.txt")

        assert len(client.list_objects(bucket, "p/")) == 4
        written = client.download_prefix(bucket, "p/", tmp_path / "dl", suffixes=(".jpg",))
        assert len(written) == 3
