"""Module entrypoint to support `python -m gridironlabs`."""

from __future__ import annotations

from gridironlabs.main import main

if __name__ == "__main__":
    raise SystemExit(main())
