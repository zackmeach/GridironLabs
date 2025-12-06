from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import AppPaths


class _CorrelationFilter(logging.Filter):
    """
    Ensures a correlation_id field exists for structured log lines.
    """

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401 - simple guard
        if not hasattr(record, "correlation_id"):
            record.correlation_id = "app"  # type: ignore[attr-defined]
        return True


def _ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def setup_logging(paths: AppPaths, level: str = "INFO") -> logging.Logger:
    """
    Configure console + rotating file logging with a minimal structured format.
    """

    logger = logging.getLogger("gridironlabs")
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return logger

    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    root_logger.setLevel(log_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(correlation_id)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    correlation_filter = _CorrelationFilter()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(correlation_filter)

    _ensure_directory(paths.logs)
    file_handler = RotatingFileHandler(
        paths.logs / "gridironlabs.log",
        maxBytes=512_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(correlation_filter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    logger.propagate = True

    logging.captureWarnings(True)
    return logger
