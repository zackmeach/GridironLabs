from __future__ import annotations

import sys
from typing import Callable

from gridironlabs.app import run
from gridironlabs.core import AppConfig, load_config, setup_logging


def _install_exception_hook(report_fn: Callable[[BaseException], None]) -> None:
    def handle_exception(exc_type, exc_value, exc_traceback):  # type: ignore[override]
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        report_fn(exc_value)

    sys.excepthook = handle_exception


def main() -> None:
    config: AppConfig = load_config()
    logger = setup_logging(config.paths)

    def report(exc: BaseException) -> None:
        logger.exception("Uncaught exception", exc_info=(exc.__class__, exc, exc.__traceback__))

    _install_exception_hook(report)
    logger.info("Launching Gridiron Labs UI shell", extra={"correlation_id": "startup"})
    run(config, logger)


if __name__ == "__main__":
    main()
