# solar-report-utils

Shared building blocks for the solar report builders (thermographic, EL, IV).
Centralizes code that was previously copy-pasted across the three repos:

- **`exceptions`** — `ProcessingError` hierarchy (`S3DownloadError`, `S3UploadError`,
  `ImageProcessingError`, `ReportGenerationError`, `InvalidInputError`).
- **`logging`** — `setup_logging()` / `get_logger()` (JSON for CloudWatch).
- **`config`** — `BaseReportSettings` (the `SOLAR_` env convention) and
  `get_bucket_suffix()`.
- **`s3`** — `BaseS3Client` (boto3 setup with timeouts + retries, plus generic
  `download_file` / `upload_file` / `list_objects` / `download_prefix`) and
  `parse_s3_uri()`.

## Usage

```python
from solar_report_utils import BaseReportSettings, BaseS3Client, setup_logging, ProcessingError

class Settings(BaseReportSettings):
    project_id: str
    reports_bucket: str = "solar-reports-prod"

class S3Client(BaseS3Client):
    def download_report_inputs(self, ...):
        return self.download_file(...)  # built on the shared primitives
```

## Install

Builders pin this library by commit in their Dockerfile / requirements:

```
pip install "git+https://github.com/caxaxa/solar-report-utils.git@<sha>"
```

## Develop

```bash
pip install -e ".[dev]"
pytest
```
