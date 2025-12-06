"""Structured logging helpers."""

from __future__ import annotations

import json
import logging
import logging.config
import sys
from dataclasses import asdict, dataclass
from typing import Any

from gridironlabs.core.config import AppConfig, AppPaths


@dataclass(frozen=True)
class LogContext:
    correlation_id: str | None = None
    component: str | None = None

    def extra(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


class JsonFormatter(logging.Formatter):
    """Lightweight JSON formatter without extra dependencies."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        payload.update(
            {k: v for k, v in record.__dict__.items() if k not in logging.LogRecord.__dict__}
        )
        return json.dumps(payload)


def configure_logging(paths: AppPaths, config: AppConfig) -> logging.Logger:
    """Initialize console + rotating file logging with structured output."""
    paths.logs.mkdir(parents=True, exist_ok=True)
    log_path = paths.logs / "gridironlabs.log"

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JsonFormatter,
            },
            "console": {
                "format": "%(levelname)s %(name)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": config.log_level,
                "formatter": "console",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": config.log_level,
                "formatter": "json",
                "filename": str(log_path),
                "maxBytes": 5 * 1024 * 1024,
                "backupCount": 3,
            },
        },
        "loggers": {
            "gridironlabs": {
                "handlers": ["console", "file"],
                "level": config.log_level,
                "propagate": False,
            },
        },
        "root": {"level": "WARNING", "handlers": ["console"]},
    }

    logging.config.dictConfig(logging_config)
    logger = logging.getLogger("gridironlabs")
    logger.debug("Logging configured", extra={"env": config.environment, "log_path": str(log_path)})
    return logger
