"""Structured logging configuration for CloudWatch (shared across builders)."""

import logging
import sys

from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO", json_format: bool = True) -> None:
    """Configure root logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_format: If True, emit JSON lines (CloudWatch-friendly); otherwise
            a human-readable format for local development.
    """
    root = logging.getLogger()
    root.setLevel(log_level.upper())

    for handler in root.handlers[:]:
        root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level.upper())

    if json_format:
        formatter: logging.Formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger."""
    return logging.getLogger(name)
