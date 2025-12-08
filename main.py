"""Convenience entrypoint to launch the Gridiron Labs UI shell."""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    # Allow running the app directly from a fresh checkout before install.
    repo_root = Path(__file__).resolve().parent
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def main() -> int:
    _ensure_src_on_path()
    from gridironlabs.main import main as _app_main

    return _app_main()


if __name__ == "__main__":
    raise SystemExit(main())

