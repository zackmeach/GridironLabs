from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _load_env_file(path: Path) -> Dict[str, str]:
    """
    Tiny .env reader to avoid extra dependencies.
    """

    if not path.exists():
        return {}

    env: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        env[key.strip()] = value.strip()
    return env


@dataclass(frozen=True)
class AppPaths:
    """
    Collection of filesystem locations used throughout the app.
    """

    root: Path
    data_root: Path
    raw_data: Path
    interim_data: Path
    processed_data: Path
    external_data: Path
    resources: Path
    logs: Path

    @staticmethod
    def default(root: Path | None = None, data_root: Path | None = None) -> "AppPaths":
        base = root or Path(__file__).resolve().parents[3]
        resolved_data = data_root or (base / "data")
        return AppPaths(
            root=base,
            data_root=resolved_data,
            raw_data=resolved_data / "raw",
            interim_data=resolved_data / "interim",
            processed_data=resolved_data / "processed",
            external_data=resolved_data / "external",
            resources=base / "src" / "gridironlabs" / "resources",
            logs=base / "logs",
        )


@dataclass(frozen=True)
class FeatureFlags:
    """
    Simple toggle set for in-progress features.
    """

    enable_scraping: bool = False
    enable_live_refresh: bool = False


@dataclass(frozen=True)
class AppConfig:
    """
    Aggregated application configuration to wire into services.
    """

    paths: AppPaths
    flags: FeatureFlags
    offline_mode: bool = False


def load_config(root: Path | None = None, env_path: Path | None = None) -> AppConfig:
    """
    Build a configuration object honoring .env and environment overrides.
    """

    base_root = Path(os.environ.get("GRIDIRONLABS_ROOT", root or Path(__file__).resolve().parents[3]))
    env_file_path = env_path or (base_root / ".env")
    env_from_file = _load_env_file(env_file_path)
    env: Dict[str, str] = {**env_from_file, **os.environ}

    data_root_override = Path(env["GRIDIRONLABS_DATA_ROOT"]) if "GRIDIRONLABS_DATA_ROOT" in env else None
    flags = FeatureFlags(
        enable_scraping=_parse_bool(env.get("GRIDIRONLABS_ENABLE_SCRAPING")),
        enable_live_refresh=_parse_bool(env.get("GRIDIRONLABS_ENABLE_LIVE_REFRESH")),
    )
    offline_mode = _parse_bool(env.get("GRIDIRONLABS_OFFLINE"))

    paths = AppPaths.default(root=base_root, data_root=data_root_override)
    return AppConfig(paths=paths, flags=flags, offline_mode=offline_mode)
