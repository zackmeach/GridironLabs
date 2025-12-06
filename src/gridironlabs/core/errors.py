"""Shared exceptions."""

from __future__ import annotations


class GridironLabsError(Exception):
    """Base application error."""


class MissingDependencyError(GridironLabsError):
    """Raised when optional dependencies like PySide6 or nflreadpy are absent."""


class DataValidationError(GridironLabsError):
    """Raised when incoming data fails schema validation."""


class NotFoundError(GridironLabsError):
    """Raised when an entity id cannot be resolved."""
