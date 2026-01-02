"""Shared ColumnSpec used by both widget tables and QTableView surfaces."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt


@dataclass(frozen=True)
class ColumnSpec:
    key: str
    label: str
    width: int
    alignment: Qt.Alignment


__all__ = ["ColumnSpec"]

