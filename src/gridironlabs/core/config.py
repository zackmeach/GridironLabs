"""Configuration and path helpers for Gridiron Labs."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

try:  # Optional dependency; do not fail if missing during scaffolding.
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - guard for environments without python-dotenv
    load_dotenv = None


def _as_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppPaths:
    """Centralized filesystem locations used throughout the app."""

    root: Path
    data_raw: Path
    data_interim: Path
    data_processed: Path
    data_external: Path
    cache: Path
    logs: Path

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "AppPaths":
        env = dict(env or os.environ)
        root = Path(env.get("GRIDIRONLABS_ROOT", Path.cwd())).resolve()
        data_dir = root / "data"
        return cls(
            root=root,
            data_raw=data_dir / "raw",
            data_interim=data_dir / "interim",
            data_processed=data_dir / "processed",
            data_external=data_dir / "external",
            cache=root / ".cache",
            logs=root / "logs",
        )

    def ensure_directories(self) -> None:
        for path in (
            self.data_raw,
            self.data_interim,
            self.data_processed,
            self.data_external,
            self.cache,
            self.logs,
        ):
            path.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class AppConfig:
    """Typed runtime configuration."""

    environment: str
    enable_scraping: bool
    enable_live_refresh: bool
    ui_theme: str
    http_timeout_seconds: float
    max_http_retries: int
    retry_backoff_seconds: float
    default_schema_version: str
    log_level: str

    @classmethod
    def from_env(cls, paths: AppPaths, env: Mapping[str, str] | None = None) -> "AppConfig":
        env = dict(env or os.environ)
        return cls(
            environment=env.get("GRIDIRONLABS_ENV", "dev"),
            enable_scraping=_as_bool(env.get("GRIDIRONLABS_ENABLE_SCRAPING"), default=False),
            enable_live_refresh=_as_bool(env.get("GRIDIRONLABS_ENABLE_LIVE_REFRESH"), default=False),
            ui_theme=env.get("GRIDIRONLABS_UI_THEME", "dark"),
            http_timeout_seconds=float(env.get("GRIDIRONLABS_HTTP_TIMEOUT", "10")),
            max_http_retries=int(env.get("GRIDIRONLABS_MAX_HTTP_RETRIES", "3")),
            retry_backoff_seconds=float(env.get("GRIDIRONLABS_RETRY_BACKOFF", "0.5")),
            default_schema_version=env.get("GRIDIRONLABS_SCHEMA_VERSION", "v0"),
            log_level=env.get("GRIDIRONLABS_LOG_LEVEL", "INFO"),
        )


def load_config(paths: AppPaths, env_file: str | None = ".env") -> AppConfig:
    """Load configuration from environment and optional .env file."""
    if env_file and load_dotenv:
        env_path = Path(env_file)
        if not env_path.is_absolute():
            env_path = paths.root / env_file
        if env_path.exists():
            load_dotenv(env_path)
    config = AppConfig.from_env(paths)
    paths.ensure_directories()
    return config
