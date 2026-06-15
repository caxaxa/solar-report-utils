"""Shared configuration base for the solar report builders.

Each builder defines its own ``Settings(BaseReportSettings)`` adding the fields
it needs. The base centralizes the ``SOLAR_`` env convention and the dev/prod
bucket-suffix helper that were previously copy-pasted across builders.
"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


def get_bucket_suffix() -> str:
    """Return ``dev`` or ``prod`` based on the ENVIRONMENT variable."""
    return "dev" if os.getenv("ENVIRONMENT", "prod").lower() == "dev" else "prod"


class BaseReportSettings(BaseSettings):
    """Common settings base.

    All settings can be overridden via ``SOLAR_``-prefixed environment
    variables (e.g. ``SOLAR_PROJECT_ID=abc123``).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SOLAR_",
        case_sensitive=False,
        extra="ignore",
    )

    aws_region: str = "us-east-2"
