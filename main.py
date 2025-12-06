"""Convenience entrypoint to launch the Gridiron Labs UI shell."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    # Allow running the app directly from a fresh checkout before install.
    repo_root = Path(__file__).resolve().parent
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def main() -> None:
    _ensure_src_on_path()
    # Delegate to the package entrypoint.
    runpy.run_module("gridironlabs.main", run_name="__main__")


if __name__ == "__main__":
    main()

