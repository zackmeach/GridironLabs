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
from gridironlabs.data.schemas import SCHEMA_REGISTRY
from gridironlabs.data.sources.nflreadpy_adapter import NFLReadPyAdapter
from gridironlabs.data.sources.pfr_scraper import PfrScraper, ScrapeConfig


def main() -> None:
    paths = AppPaths.from_env()
    config = load_config(paths)
    repo = ParquetSummaryRepository(
        root=paths.data_processed,
        schema_version=SCHEMA_REGISTRY["players:v0"],
    )
    nfl_source = NFLReadPyAdapter(enabled=config.enable_scraping)
    pfr_source = PfrScraper(config=ScrapeConfig(), enabled=config.enable_scraping)
    raise NotImplementedError(
        "Wire data refresh flow: fetch, merge, validate, and persist Parquet tables."
    )


if __name__ == "__main__":
    main()
