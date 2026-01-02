"""Base table models for OOTP-style QTableView surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor, QFont

from gridironlabs.ui.table.columns import ColumnSpec


class RowRole:
    """Semantic row roles for styling/behavior."""

    DATA = "data"
    GROUP = "group"
    SUMMARY = "summary"


ROW_ROLE = Qt.UserRole + 100
SECONDARY_TEXT_ROLE = Qt.UserRole + 101
INTENT_ROLE = Qt.UserRole + 102
TIER_ROLE = Qt.UserRole + 103


@dataclass(frozen=True)
class TableRow:
    values: Mapping[str, Any]
    row_role: str = RowRole.DATA
    secondary: Mapping[str, str] | None = None  # optional per-column secondary text
    intent: str | None = None
    tier: str | None = None


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


class ColumnTableModel(QAbstractTableModel):
    """Simple column-spec-driven model for demos and early migration."""

    def __init__(self, *, columns: Sequence[ColumnSpec], rows: Sequence[TableRow]) -> None:
        super().__init__()
        self._columns = list(columns)
        self._rows = list(rows)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802 - Qt API
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802 - Qt API
        if parent.isValid():
            return 0
        return len(self._columns)

    def headerData(  # noqa: N802 - Qt API
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.DisplayRole,
    ) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if 0 <= section < len(self._columns):
                return self._columns[section].label
        return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:  # noqa: N802 - Qt API
        if not index.isValid():
            return None

        row = self._rows[index.row()]
        col = self._columns[index.column()]
        value = row.values.get(col.key)

        if role == Qt.DisplayRole:
            return _fmt(value)

        if role == Qt.TextAlignmentRole:
            return int(col.alignment)

        if role == ROW_ROLE:
            return row.row_role

        if role == SECONDARY_TEXT_ROLE:
            if row.secondary and col.key in row.secondary:
                return row.secondary[col.key]
            return None

        if role == Qt.FontRole and row.row_role in {RowRole.GROUP, RowRole.SUMMARY}:
            font = QFont()
            font.setBold(True)
            return font

        if role == Qt.ForegroundRole and row.row_role == RowRole.GROUP:
            return QColor("#9ca3af")

        return None

    @property
    def columns(self) -> Sequence[ColumnSpec]:
        return self._columns


__all__ = [
    "ColumnTableModel",
    "RowRole",
    "TableRow",
    "ROW_ROLE",
    "SECONDARY_TEXT_ROLE",
    "INTENT_ROLE",
    "TIER_ROLE",
]

