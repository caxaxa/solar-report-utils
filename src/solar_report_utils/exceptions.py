"""Shared exception hierarchy for the solar report builders."""


class ProcessingError(Exception):
    """Base exception for all report-processing errors."""


class S3DownloadError(ProcessingError):
    """Error downloading files from S3."""


class S3UploadError(ProcessingError):
    """Error uploading files to S3."""


class ImageProcessingError(ProcessingError):
    """Error during image processing operations."""


class ReportGenerationError(ProcessingError):
    """Error during report generation."""


class InvalidInputError(ProcessingError):
    """Invalid input data or parameters."""
