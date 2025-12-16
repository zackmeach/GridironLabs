"""Packaged visual assets and access helpers.

Prefer using these helpers instead of building resource paths relative to
`__file__`. That keeps resource access working when the package is installed
from a wheel (and potentially zipped in the future).
"""

from __future__ import annotations

from contextlib import contextmanager
from importlib import resources
from pathlib import Path
from typing import Iterator


def read_text(*relative_parts: str, encoding: str = "utf-8") -> str:
    """Read a UTF-8 text file from `gridironlabs.resources`."""
    return resources.files(__package__).joinpath(*relative_parts).read_text(encoding=encoding)


def read_bytes(*relative_parts: str) -> bytes:
    """Read a binary file from `gridironlabs.resources`."""
    return resources.files(__package__).joinpath(*relative_parts).read_bytes()


@contextmanager
def as_file(*relative_parts: str) -> Iterator[Path]:
    """Yield an on-disk path to a packaged resource.

    This supports resources coming from a wheel, where the underlying resource
    might not already exist as a normal file on disk.
    """
    traversable = resources.files(__package__).joinpath(*relative_parts)
    with resources.as_file(traversable) as path:
        yield Path(path)


__all__ = ["as_file", "read_bytes", "read_text"]
