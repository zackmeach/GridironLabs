"""Placeholder data refresh script.

Intended responsibilities:
- Pull from nflreadpy and PFR adapters.
- Normalize/de-duplicate entity ids.
- Validate against Parquet schemas before writing to `data/processed`.
- Record provenance and schema version metadata.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from gridironlabs.core.config import AppPaths, load_config
from gridironlabs.data.repository import ParquetSummaryRepository
from gridironlabs.data.sources.nflreadpy_adapter import NFLReadPyAdapter
from gridironlabs.data.sources.pfr_scraper import PfrScraper, ScrapeConfig


def main() -> int:
    paths = AppPaths.from_env()
    config = load_config(paths)
    repo = ParquetSummaryRepository(paths.data_processed, schema_version=config.default_schema_version)
    nfl_source = NFLReadPyAdapter(enabled=config.enable_scraping)
    pfr_source = PfrScraper(config=ScrapeConfig(), enabled=config.enable_scraping)
    print(
        "Not implemented: wire data refresh flow (fetch, merge, validate, persist Parquet tables).\n"
        f"- output: {paths.data_processed}\n"
        f"- schema_version: {config.default_schema_version}\n"
        f"- scraping_enabled: {config.enable_scraping}\n"
        f"- adapters: {nfl_source.__class__.__name__}, {pfr_source.__class__.__name__}\n"
        f"- repository: {repo.__class__.__name__}"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
