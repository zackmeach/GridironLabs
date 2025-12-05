 from __future__ import annotations
 
 from dataclasses import dataclass
 from pathlib import Path
 
 
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
 
     @staticmethod
     def default(root: Path | None = None) -> "AppPaths":
        base = root or Path(__file__).resolve().parents[3]
         data_root = base / "data"
         return AppPaths(
             root=base,
             data_root=data_root,
             raw_data=data_root / "raw",
             interim_data=data_root / "interim",
             processed_data=data_root / "processed",
             external_data=data_root / "external",
             resources=base / "src" / "gridironlabs" / "resources",
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
     flags: FeatureFlags = FeatureFlags()
 
 
 def load_config(root: Path | None = None) -> AppConfig:
     """
     Build a default configuration object.
     """
 
     return AppConfig(paths=AppPaths.default(root=root))
