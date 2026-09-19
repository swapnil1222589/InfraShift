"""Structured logging configuration for InfraShift."""
from __future__ import annotations

import logging
import sys
from typing import Any


def configure_logging(log_level: str = "INFO") -> None:
    """Configure application-wide structured logging."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s [%(request_id)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(numeric_level)
    root.handlers.clear()
    root.addHandler(handler)

    # Reduce noise from third-party libraries
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


class RequestIdFilter(logging.Filter):
    """Inject request_id into log records."""

    def __init__(self, request_id: str = "-") -> None:
        super().__init__()
        self.request_id = request_id

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        record.request_id = self.request_id  # type: ignore[attr-defined]
        return True


def get_logger(name: str, **extra: Any) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)
