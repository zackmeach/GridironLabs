"""Entry point for launching Gridiron Labs."""

from __future__ import annotations

import sys

from gridironlabs.core.config import AppPaths, load_config
from gridironlabs.core.logging import configure_logging
from gridironlabs.ui.app import GridironLabsApplication


def main() -> int:
    paths = AppPaths.from_env()
    config = load_config(paths)
    logger = configure_logging(paths, config)
    app = GridironLabsApplication(config=config, paths=paths, logger=logger)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
