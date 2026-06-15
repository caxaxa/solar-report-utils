"""solar-report-utils — shared building blocks for the solar report builders.

Centralizes the exception hierarchy, structured logging, settings base, and the
generic S3 client that were previously copy-pasted across the thermographic, EL,
and IV report builders.
"""

from .config import BaseReportSettings, get_bucket_suffix
from .exceptions import (
    ImageProcessingError,
    InvalidInputError,
    ProcessingError,
    ReportGenerationError,
    S3DownloadError,
    S3UploadError,
)
from .logging import get_logger, setup_logging
from .s3 import BaseS3Client, parse_s3_uri

__version__ = "0.1.0"

__all__ = [
    "BaseReportSettings",
    "get_bucket_suffix",
    "ProcessingError",
    "S3DownloadError",
    "S3UploadError",
    "ImageProcessingError",
    "ReportGenerationError",
    "InvalidInputError",
    "setup_logging",
    "get_logger",
    "BaseS3Client",
    "parse_s3_uri",
    "__version__",
]
